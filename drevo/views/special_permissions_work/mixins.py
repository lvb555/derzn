from django.db.models import Count, F, QuerySet, Case, When, IntegerField, Q
from django.shortcuts import get_object_or_404
from drevo.models import SpecialPermissions, SettingsOptions, Znanie, Category
from drevo.relations_tree import get_knowledges_by_categories


class CandidatesMixin:
    """
        Миксин с методами получения кандидатов в эксперты и руководители
    """
    model = SpecialPermissions

    def _selection_of_candidates(self, selection_param: SettingsOptions, candidates: dict) -> dict:
        """
            Метод для фильтрации данных кандидатов с целью отбора тех,
            которые соответствуют установленному параметру
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
            name: <str:author_name>, categories: {<int:category_pk>: [<int:knowledge_count>, <int:expertise_count>]...}
            }...
            }
        """
        min_count_to_transition = get_object_or_404(SettingsOptions, name='Минимальный порог перехода в руководители')

        # Получаем список всех опубликованных знаний у которых есть автор, которых является экспертом
        knowledge = (
            Znanie.objects
            .select_related('author', 'tz', 'author__user_author').prefetch_related('knowledge_status')
            .filter(is_published=True, author__isnull=False, author__user_author__isnull=False,
                    author__user_author__is_expert=True, author__user_author__is_director=False,
                    tz__is_systemic=False, knowledge_status__status='PUB')
        )
        # Получаем список всех опубликованных экспертиз
        expertise = (
            Znanie.objects
            .select_related('expert', 'tz').prefetch_related('knowledge_status')
            .filter(is_published=True, expert__isnull=False, expert__is_director=False,
                    tz__is_systemic=False, knowledge_status__status='PUB')
        )

        queryset = (knowledge | expertise).distinct()

        # Берём из списка только те знания и экспертизы у которых есть категория
        knowledge_with_cat = (
            queryset
            .filter(category__isnull=False)
            .values(user_pk=F('author__user_author_id'), user_name=F('author__name'), category_pk=F('category_id'),
                    expert_pk=F('expert_id'), first_name=F('expert__first_name'), last_name=F('expert__last_name'))
            .annotate(cnt=Count('category_pk'))
        )

        # Берём из списка только те знания у которых нет категории
        knowledge_without_cat = queryset.filter(category__isnull=True)

        # Получаем категории для знаний у которых их нет
        without_cat_data = self._get_additional_knowledge(knowledge=knowledge_without_cat)

        candidates = dict()

        for knowledge_data in knowledge_with_cat:
            author, user_name, category, expert_pk, first_name, last_name, cnt = knowledge_data.values()
            author_pk = expert_pk if not author else author
            name = f'{first_name} {last_name}' if not user_name else user_name
            if author_pk in candidates.keys():
                candidate_data = candidates[author_pk]['categories']
                if category in candidate_data.keys():
                    if author:
                        candidate_data[category][0] += cnt
                    else:
                        candidate_data[category][1] += cnt
                    continue
                candidate_data[category] = [0, cnt] if not author else [cnt, 0]
                continue
            candidates[author_pk] = dict(name=name, categories={category: [0, cnt] if not author else [cnt, 0]})

        for know, cat in without_cat_data:
            author_pk = know.author.user_author_id
            author_id = author_pk if author_pk else know.expert_id
            if author_id not in candidates.keys():
                author_name = know.author.name
                name = author_name if author_name else f'{know.expert.first_name} {know.expert.last_name}'
                candidates[author_id] = dict(name=name, categories=dict())
                candidates[author_id]['categories'] = {cat.pk: 1}
                continue
            candidate_categories = candidates[author_id]['categories']
            if cat.pk in candidate_categories.keys():
                if know.author:
                    candidate_categories[cat.pk][0] += 1
                else:
                    candidate_categories[cat.pk][1] += 1
            else:
                candidate_categories[cat.pk] = [0, 1] if not know.author else [1, 0]

        candidates = self._selection_of_candidates(min_count_to_transition, candidates)
        return candidates

    def get_user_competencies_data(self, user_pk: int) -> dict:
        """
            Метод для получения данных о всех компетенциях пользователя (как в роли эксперта так и руководителя)
            Результирующие  данные:\n
            {<int:category_pk>: [<int:knowledge_count>, <int:expertise_count>]...}
        """

        # Получаем список всех опубликованных знаний пользователя
        knowledge = (
            Znanie.objects
            .select_related('author', 'tz', 'author__user_author').prefetch_related('knowledge_status')
            .filter(is_published=True, author__user_author_id=user_pk,
                    tz__is_systemic=False, knowledge_status__status='PUB')
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
            .annotate(is_expertise=Case(When(expert__isnull=False, then=1), default=0, output_field=IntegerField()))
            .values('category_id', 'is_expertise')
            .annotate(cnt=Count('category_id'))
        )

        # Берём из списка только те знания у которых нет категории
        knowledge_without_cat = queryset.filter(category__isnull=True)

        # Получаем категории для знаний у которых их нет
        without_cat_data = self._get_additional_knowledge(knowledge=knowledge_without_cat)

        competencies_data = dict()

        for knowledge_data in knowledge_with_cat:
            category, is_expertise, cnt = knowledge_data.values()
            if category not in competencies_data.keys():
                competencies_data[category] = [0, cnt] if is_expertise else [cnt, 0]
                continue
            if is_expertise:
                competencies_data[category][1] += cnt
            else:
                competencies_data[category][0] += cnt

        for know, cat in without_cat_data:
            if (category := cat.pk) in competencies_data.keys():
                if know.author:
                    competencies_data[category][0] += 1
                else:
                    competencies_data[category][1] += 1
            else:
                competencies_data[category] = [0, 1] if not know.author else [1, 0]
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
            .select_related('author', 'tz', 'author__user_author').prefetch_related('knowledge_status')
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
                if know.knowledge_status.status == 'PUB_PRE':
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
