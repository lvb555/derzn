from django.db.models import Count, F, QuerySet, Case, When, IntegerField, Q
from django.shortcuts import get_object_or_404
from drevo.models import SpecialPermissions, SettingsOptions, Znanie, Category
from drevo.relations_tree import get_knowledges_by_categories
from users.models import User


class CandidatesMixin:
    """
        Миксин с методами получения кандидатов в эксперты и руководители
    """
    model = SpecialPermissions

    def _selection_of_candidates(self, selection_param: SettingsOptions, candidates: dict, admin: bool = False) -> dict:
        """
            Метод для фильтрации данных кандидатов с целью отбора тех,
            которые соответствуют установленному параметру
            admin = True (если фильтруются кандидаты в руководители)
        """
        param = int(selection_param.default_param)
        candidates_without_cat = list()
        for candidate_pk, data in candidates.items():
            drop_data = [
                cat_pk for cat_pk, cnt in data['categories'].items()
                if (sum(cnt) if isinstance(cnt, list) else cnt) < param
            ]
            if not drop_data:
                continue
            for category_pk in drop_data:
                del candidates[candidate_pk]['categories'][category_pk]
            if not candidates[candidate_pk]['categories']:
                candidates_without_cat.append(candidate_pk)
        if candidates_without_cat:
            for candidate_pk in candidates_without_cat:
                del candidates[candidate_pk]

        # Проверка на наличие компетенции в какой либо категории из полученных данных.
        # Если такие есть, то обрасываем их из текущих данных кандидатов.
        # Если категорий у кандидата вообще не остаётся, то убираем кандидата из данных.
        data_for_drop = list()
        for author in candidates.keys():
            author_data = candidates.get(author)
            if admin:
                cur_competencies = (
                    self.model.objects
                        .filter(expert_id=author, admin_competencies__in=list(author_data['categories'].keys()))
                        .values_list('admin_competencies', flat=True)
                )
            else:
                cur_competencies = (
                    self.model.objects
                        .filter(expert_id=author, categories__in=list(author_data['categories'].keys()))
                        .values_list('categories', flat=True)
                )
            if not cur_competencies.exists():
                continue
            for category in cur_competencies:
                del author_data['categories'][category]
            if not author_data['categories']:
                data_for_drop.append(author)
        if data_for_drop:
            for author in data_for_drop:
                del candidates[author]
        return candidates

    @staticmethod
    def _get_additional_knowledge(knowledge: QuerySet) -> list:
        """
            Метод для получения категорий для дополнительных знаний (знаний без категорий)
            Результирующие  данные: \n
            [(knowledge, category), (knowledge, category)...]
        """
        without_cat_data = list()
        _, zn = get_knowledges_by_categories(knowledge)
        for kn_obj in knowledge:
            for cat, data in zn.items():
                if kn_obj in data.get('additional'):
                    without_cat_data.append((kn_obj, get_object_or_404(Category, name=cat)))
                    break
        return without_cat_data

    def get_all_candidates(self) -> dict:
        """
            Метод для получения словаря с кандидатами
        """
        experts = self.get_expert_candidates()
        admins = self.get_admin_candidates()
        return dict(experts=experts, admins=admins)

    def get_expert_candidates(self) -> dict:
        """
            Метод для получения кандидатов в эксперты.
            Результирующие  данные: \n
            {<int:author_pk>: {name: <str:author_name>, categories: {<int:category_pk>: <int:category_count>...}}...}
        """
        min_count_to_transition = get_object_or_404(SettingsOptions, name='Минимальный порог перехода в эксперты')

        # Получаем список всех опубликованных предзнаний и знаний (если такие имеются) у которых есть автор
        knowledge = (
            Znanie.objects
            .select_related('author', 'tz', 'author__user_author').prefetch_related('knowledge_status')
            .filter(Q(knowledge_status__status='PUB_PRE') | Q(knowledge_status__status='PUB'),
                    is_published=True, author__isnull=False, author__user_author__isnull=False, tz__is_systemic=False)
        )
        # Берём из списка только те знания у которых есть категория
        knowledge_with_cat = (
            knowledge
            .filter(category__isnull=False)
            .values(user_pk=F('author__user_author_id'), user_name=F('author__name'), category_pk=F('category_id'))
            .annotate(cnt=Count('category_pk'))
        )
        # Берём из списка только те знания у которых нет категории
        knowledge_without_cat = knowledge.filter(category__isnull=True)

        # Получаем категории для знаний у которых их нет
        without_cat_data = self._get_additional_knowledge(knowledge=knowledge_without_cat)

        candidates = {
            elm.get('user_pk'): dict(name=elm.get('user_name'), categories=dict()) for elm in knowledge_with_cat
        }
        for knowledge_data in knowledge_with_cat:
            author, _, category, cnt = knowledge_data.values()
            candidates[author]['categories'].update({category: cnt})

        for know, cat in without_cat_data:
            if (author_id := know.author.user_author_id) not in candidates.keys():
                candidates[author_id] = dict(name=know.author.name, categories=dict())
                candidates[author_id]['categories'] = {cat.pk: 1}
                continue
            candidate_categories = candidates[author_id]['categories']
            if cat.pk in candidate_categories.keys():
                candidate_categories[cat.pk] += 1
            else:
                candidate_categories[cat.pk] = 1

        candidates = self._selection_of_candidates(min_count_to_transition, candidates)
        return candidates

    def get_admin_candidates(self) -> dict:
        """
            Метод для получения кандидатов в руководители.
            Результирующие  данные:\n
            {
            <int:author_pk>:
            {
                name: <str:author_name>, categories: {
                <int:category_pk>: [<int:preknowledge_count>, <int:knowledge_count>, <int:expertise_count>]...
                }
            }...
            }
        """
        min_count_to_transition = get_object_or_404(SettingsOptions, name='Минимальный порог перехода в руководители')

        # Получаем список всех опубликованных знаний у которых есть автор, которых является экспертом
        knowledge = (
            Znanie.objects
            .select_related('author', 'tz', 'author__user_author').prefetch_related('knowledge_status')
            .filter(Q(knowledge_status__status='PUB_PRE') | Q(knowledge_status__status='PUB'),
                    is_published=True, author__isnull=False, author__user_author__isnull=False,
                    author__user_author__is_expert=True, tz__is_systemic=False)
        )
        # Получаем список всех опубликованных экспертиз
        expertise = (
            Znanie.objects
            .select_related('expert', 'tz').prefetch_related('knowledge_status')
            .filter(is_published=True, expert__isnull=False, tz__is_systemic=False, knowledge_status__status='PUB')
        )

        queryset = (knowledge | expertise).distinct()

        # Берём из списка только те знания и экспертизы у которых есть категория
        knowledge_with_cat = (
            queryset
            .filter(category__isnull=False)
            .annotate(
                is_preknowledge=Case(
                    When(knowledge_status__status='PUB_PRE', then=1),
                    default=0,
                    output_field=IntegerField()
                )
            )
            .values(user_pk=F('author__user_author_id'), user_name=F('author__name'), category_pk=F('category_id'),
                    expert_pk=F('expert_id'), first_name=F('expert__first_name'), last_name=F('expert__last_name'),
                    is_preknowledge=F('is_preknowledge'))
            .annotate(cnt=Count('category_pk'))
        )

        candidates = dict()

        for knowledge_data in knowledge_with_cat:
            is_preknowledge, author, fullname, category, expert_pk, first_name, last_name, cnt = knowledge_data.values()
            author_pk = expert_pk if not author else author
            name = f'{first_name} {last_name}' if not fullname else fullname
            if author_pk not in candidates.keys():
                candidates[author_pk] = dict(name=name, categories={category: [0, 0, 0]})
            candidate_data = candidates[author_pk]['categories']
            if category not in candidate_data.keys():
                candidate_data[category] = [0, 0, 0]
            if is_preknowledge:
                candidate_data[category][0] += cnt
            elif author:
                candidate_data[category][1] += cnt
            else:
                candidate_data[category][2] += cnt

        # Берём из списка только те знания у которых нет категории
        knowledge_without_cat = queryset.filter(category__isnull=True)
        if len(knowledge_without_cat) != len(queryset):
            # Получаем категории для знаний у которых их нет
            without_cat_data = self._get_additional_knowledge(knowledge=knowledge_without_cat)
            for know, cat in without_cat_data:
                author_pk = know.author.user_author_id
                author_id = author_pk if author_pk else know.expert_id
                if author_id not in candidates.keys():
                    author_name = know.author.name
                    name = author_name if author_name else f'{know.expert.first_name} {know.expert.last_name}'
                    candidates[author_id] = dict(name=name, categories={cat.pk: [0, 0, 0]})
                candidate_categories = candidates[author_id]['categories']
                if cat.pk not in candidate_categories.keys():
                    candidate_categories[cat.pk] = [0, 0, 0]
                if 'PUB_PRE' in know.knowledge_status.values_list('status', flat=True):
                    candidate_categories[cat.pk][0] += 1
                elif know.author:
                    candidate_categories[cat.pk][1] += 1
                else:
                    candidate_categories[cat.pk][2] += 1

        candidates = self._selection_of_candidates(min_count_to_transition, candidates, True)
        return candidates

    def get_user_competencies_data(self, user_pk: int) -> dict:
        """
            Метод для получения данных о всех компетенциях пользователя (как в роли эксперта так и руководителя)
            Результирующие  данные:\n
            {<int:category_pk>: [<int:knowledge_count>, <int:expertise_count>, <int:preknowledge_count>]...}
        """

        # Получаем список всех опубликованных знаний пользователя
        knowledge = (
            Znanie.objects
            .select_related('author', 'tz', 'author__user_author').prefetch_related('knowledge_status')
            .filter(Q(knowledge_status__status='PUB_PRE') | Q(knowledge_status__status='PUB'),
                    is_published=True, author__user_author_id=user_pk, tz__is_systemic=False)
        )
        # Получаем список всех опубликованных экспертиз пользователя
        expertise = (
            Znanie.objects
            .select_related('expert', 'tz').prefetch_related('knowledge_status')
            .filter(is_published=True, expert_id=user_pk, tz__is_systemic=False, knowledge_status__status='PUB')
        )

        queryset = (knowledge | expertise).distinct()

        # Берём из списка только те знания и экспертизы у которых есть категория
        knowledge_with_cat = (
            queryset
            .filter(category__isnull=False)
            .annotate(
                is_expertise=Case(
                    When(expert__isnull=False, then=1), default=0, output_field=IntegerField()
                ),
                is_preknowledge=Case(
                    When(knowledge_status__status='PUB_PRE', then=1), default=0, output_field=IntegerField()
                )
            )
            .values('category_id', 'is_expertise', 'is_preknowledge')
            .annotate(cnt=Count('category_id'))
        )

        competencies_data = dict()

        for knowledge_data in knowledge_with_cat:
            category, is_expertise, is_preknowledge, cnt = knowledge_data.values()
            if category not in competencies_data.keys():
                competencies_data[category] = [0, 0, 0]
            if is_expertise:
                competencies_data[category][1] += cnt
            elif is_preknowledge:
                competencies_data[category][2] += cnt
            else:
                competencies_data[category][0] += cnt

        # Берём из списка только те знания у которых нет категории
        knowledge_without_cat = queryset.filter(category__isnull=True)
        if len(knowledge_without_cat) != len(queryset):
            # Получаем категории для знаний у которых их нет
            without_cat_data = self._get_additional_knowledge(knowledge=knowledge_without_cat)
            for know, cat in without_cat_data:
                if (category := cat.pk) not in competencies_data.keys():
                    competencies_data[category] = [0, 0, 0]
                if know.expert:
                    competencies_data[category][1] += 1
                elif 'PUB_PRE' in know.knowledge_status.values_list('status', flat=True):
                    competencies_data[category][2] += 1
                else:
                    competencies_data[category][0] += 1

        return competencies_data

    def get_expert_candidate_knowledge(self, candidate_pk: int, category_pk: int) -> dict[str, list]:
        """
            Метод для получения знаний кандидата в эксперты в рамках определённой категории
            Результирующие данные:
            {'knowledge': [(<int:pk>, <str:name), ... ], 'preknowledge': [(<int:pk>, <str:name), ... ]}
        """
        knowledge_data = {'knowledge': list(), 'preknowledge': list()}

        # Получаем все знания и предзнания кандидата
        knowledge = (
            Znanie.objects
            .select_related('author', 'tz').prefetch_related('knowledge_status')
            .filter(Q(knowledge_status__status='PUB_PRE') | Q(knowledge_status__status='PUB'),
                    is_published=True, author__user_author_id=candidate_pk, tz__is_systemic=False)
            .annotate(
                is_preknowledge=Case(
                    When(knowledge_status__status='PUB_PRE', then=1),
                    default=0,
                    output_field=IntegerField()
                )
            )
            .order_by('-date')
        )

        # Отбираем те знания у которых есть категория и значение категории текущей компетенции
        knowledge_with_cat = (
            knowledge
            .filter(category_id=category_pk)
            .values('pk', 'name', 'is_preknowledge')
        )
        # Отбираем те знания у которых категории нет (если такие имеются), чтобы её определить
        if len(knowledge_with_cat) != len(knowledge):
            knowledge_without_cat = knowledge.filter(category__isnull=True)
            without_cat_data = [
                know for know, cat in self._get_additional_knowledge(knowledge_without_cat) if cat.pk == category_pk
            ]
            for know in without_cat_data:
                if 'PUB_PRE' in know.knowledge_status.values_list('status', flat=True):
                    knowledge_data['preknowledge'].append((know.pk, know.name))
                    continue
                knowledge_data['knowledge'].append((know.pk, know.name))

        for know_info in knowledge_with_cat:
            knowledge_pk, name, is_preknowledge = know_info.values()
            if is_preknowledge:
                knowledge_data['preknowledge'].append((knowledge_pk, name))
                continue
            knowledge_data['knowledge'].append((knowledge_pk, name))
        return knowledge_data

    def get_admin_candidate_knowledge(self, candidate_pk: int, category_pk: int) -> dict[str, list]:
        """
            Метод для получения знаний кандидата в руководители в рамках определённой категории.
            Результирующие данные:
            {
            'knowledge': [(<int:pk>, <str:name), ... ],
            'preknowledge': [(<int:pk>, <str:name), ... ],
            'expertise': [(<int:pk>, <str:name), ... ]
            }
        """
        knowledge_data = {'knowledge': list(), 'preknowledge': list(), 'expertise': list()}

        # Получаем все знания, предзнания и экспертизы кандидата
        knowledge = (
            Znanie.objects
            .select_related('author', 'tz').prefetch_related('knowledge_status')
            .filter(Q(knowledge_status__status='PUB_PRE') | Q(knowledge_status__status='PUB'),
                    Q(author__user_author_id=candidate_pk) | Q(expert_id=candidate_pk),
                    is_published=True, tz__is_systemic=False)
            .annotate(
                is_preknowledge=Case(
                    When(knowledge_status__status='PUB_PRE', then=1),
                    default=0,
                    output_field=IntegerField()
                ),
                is_expertise=Case(
                    When(expert__isnull=False, then=1),
                    default=0,
                    output_field=IntegerField()
                )
            )
            .order_by('-date')
        )

        # Отбираем те знания у которых есть категория и значение категории текущей компетенции
        knowledge_with_cat = (
            knowledge
            .filter(category_id=category_pk)
            .values('pk', 'name', 'is_preknowledge', 'is_expertise')
        )
        # Отбираем те знания у которых категории нет (если такие имеются), чтобы её определить
        if len(knowledge_with_cat) != len(knowledge):
            knowledge_without_cat = knowledge.filter(category__isnull=True)
            without_cat_data = [
                know for know, cat in self._get_additional_knowledge(knowledge_without_cat) if cat.pk == category_pk
            ]
            for know in without_cat_data:
                if know.expert:
                    knowledge_data['expertise'].append((know.pk, know.name))
                elif 'PUB_PRE' in know.knowledge_status.values_list('status', flat=True):
                    knowledge_data['preknowledge'].append((know.pk, know.name))
                else:
                    knowledge_data['knowledge'].append((know.pk, know.name))

        for know_info in knowledge_with_cat:
            knowledge_pk, name, is_preknowledge, is_expertise = know_info.values()
            if is_expertise:
                knowledge_data['expertise'].append((knowledge_pk, name))
            elif is_preknowledge:
                knowledge_data['preknowledge'].append((knowledge_pk, name))
            else:
                knowledge_data['knowledge'].append((knowledge_pk, name))
        return knowledge_data


class UserPermissionsMixin:
    """
        Миксин для работы с пользователями, которые имеют особые права
    """
    model = SpecialPermissions

    @staticmethod
    def _get_additional_knowledge(knowledge: QuerySet) -> dict:
        """
            Метод для получения категорий для дополнительных знаний (знаний без категорий)
            Результирующие  данные: \n
            {knowledge1: category, knowledge2: category...}
        """
        without_cat_data = dict()
        _, zn = get_knowledges_by_categories(knowledge)
        for kn_obj in knowledge:
            for cat, data in zn.items():
                if kn_obj in data.get('additional'):
                    without_cat_data[kn_obj] = get_object_or_404(Category, name=cat)
                    break
        return without_cat_data

    def get_experts_for_delete(self, for_category=None):
        """
            Метод для получения пользователей, которые не выполняют свои обязанности как экспертов.
            for_category: Если передать категорию, то на выходе будут эксперты в рамках данной категории.

            Результирующие  данные: \n
            1. Если категория установлена
            {expert_pk: [knowledge],}
            2. Если категория не установлена
            {category_pk: experts_count,}
        """
        min_knowledge_param = get_object_or_404(
            SettingsOptions, name='Минимальное число знаний и экспертиз за период для эксперта'
        )
        min_knowledge_param = int(min_knowledge_param.default_param)

        # Получаем экспертов и их компетенции
        permissions = SpecialPermissions.objects.filter(categories__isnull=False).values('expert', 'categories')

        experts = set(perm.get('expert') for perm in permissions)

        # Получем все опубликованные знания и экспертизы экспертов
        knowledge = (
            Znanie.objects.select_related('author__user_author', 'category')
            .filter(
                Q(author__user_author__in=experts) | Q(expert__in=experts),
                is_published=True, tz__is_systemic=False, knowledge_status__status='PUB'
            )
            .annotate(
                is_expertise=Case(
                    When(expert__isnull=False, then=1),
                    default=0,
                    output_field=IntegerField()
                )
            )
        )

        experts_data = dict()

        for perm_data in permissions:
            category = perm_data.get('categories')
            expert = perm_data.get('expert')
            if category not in experts_data:
                experts_data[category] = {expert: list()}
                continue
            experts_data[category].update({expert: list()})

        # Получаем категорию для дополнительных знаний
        knowledge_without_cat = knowledge.filter(category__isnull=True)
        knowledge_without_cat = self._get_additional_knowledge(knowledge_without_cat)
        for kn in knowledge:
            if kn in knowledge_without_cat:
                kn.category = knowledge_without_cat.get(kn)

        knowledge = knowledge.filter(category__in=experts_data)

        for kn in knowledge:
            category_data = experts_data[kn.category.id]
            expert = kn.expert.id if kn.is_expertise else kn.author.user_author.id
            if expert not in category_data:
                continue
            expert_knowledge = category_data[expert]
            expert_knowledge.append(kn)
            if len(expert_knowledge) >= min_knowledge_param:
                del experts_data[kn.category.id][expert]

        if for_category:
            return experts_data.get(for_category.id)
        return {cat_id: len(data) for cat_id, data in experts_data.items() if len(data) > 0}

    @staticmethod
    def get_editors_data(last_name: str = None):
        """
            Метод для получения данных о редакторах
            Результирующие  данные: \n
            [(editor_pk, editor_name, knowledge_edited_count), ]
        """
        if last_name:
            return (
                User.objects
                .filter(is_redactor=True, last_name__icontains=last_name, expert__editor=True)
                .annotate(knowledge_edited=Count('redactor'))
                .order_by('first_name')
            )
        return (
            User.objects
            .filter(is_redactor=True, expert__editor=True)
            .annotate(knowledge_edited=Count('redactor'))
            .order_by('first_name')
        )

    def get_admins_for_delete(self, for_category=None):
        """
            Метод для получения данных пользователей с правами руководителя.
            for_category: Если передать категорию, то на выходе будут руководители в рамках данной категории.

            Результирующие  данные: \n
            1. Если категория установлена
            {admin_pk: knowledge_count,}
            2. Если категория не установлена
            {category_pk: admins_count,}
        """
        # Получаем руководителей и их компетенции
        permissions = (
            SpecialPermissions.objects.filter(admin_competencies__isnull=False).values('expert', 'admin_competencies')
        )
        admins = set(perm.get('expert') for perm in permissions)

        # Получем все обработанные знания руководителя
        knowledge = (
            Znanie.objects
            .select_related('category')
            .filter(
                director__in=admins, is_published=True, tz__is_systemic=False, knowledge_status__status='PUB'
            )
        )

        admins_data = dict()

        for perm_data in permissions:
            category = perm_data.get('admin_competencies')
            admin = perm_data.get('expert')
            if category not in admins_data:
                admins_data[category] = {admin: 0}
                continue
            admins_data[category].update({admin: 0})

        # Получаем категорию для дополнительных знаний
        knowledge_without_cat = knowledge.filter(category__isnull=True)
        knowledge_without_cat = self._get_additional_knowledge(knowledge_without_cat)
        for kn in knowledge:
            if kn in knowledge_without_cat:
                kn.category = knowledge_without_cat.get(kn)

        knowledge = knowledge.filter(category__in=admins_data)

        for kn in knowledge:
            category_data = admins_data[kn.category.id]
            admin = kn.director.id
            if admin not in category_data:
                continue
            category_data[admin] += 1

        if for_category:
            return admins_data.get(for_category.id)
        return {cat_id: len(data) for cat_id, data in admins_data.items() if len(data) > 0}
