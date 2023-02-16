from django.db.models import Count, F
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
            drop_data = [cat_pk for cat_pk, cnt in data['categories'].items() if cnt < param]
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

        # Получаем список всех опубликованных предзнаний у которых есть автор и он не является экспертом
        knowledge = (
            Znanie.objects
            .select_related('author', 'tz', 'author__user_author').prefetch_related('knowledge_status')
            .filter(is_published=True, author__isnull=False, author__user_author__isnull=False,
                    author__user_author__is_expert=False, tz__is_systemic=False, knowledge_status__status='PUB_PRE')
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
        without_cat_data = list()
        _, zn = get_knowledges_by_categories(knowledge_without_cat)
        for kn_obj in knowledge_without_cat:
            for cat, data in zn.items():
                if kn_obj in data.get('additional'):
                    without_cat_data.append((kn_obj, get_object_or_404(Category, name=cat)))
                    break

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
            {<int:author_pk>: {name: <str:author_name>, categories: {<int:category_pk>: <int:category_count>...}}...}
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
        knowledge_without_cat = knowledge.filter(category__isnull=True)

        # Получаем категории для знаний у которых их нет
        without_cat_data = list()
        _, zn = get_knowledges_by_categories(knowledge_without_cat)
        for kn_obj in knowledge_without_cat:
            for cat, data in zn.items():
                if kn_obj in data.get('additional'):
                    without_cat_data.append((kn_obj, get_object_or_404(Category, name=cat)))
                    break

        candidates = dict()
        for knowledge_data in knowledge_with_cat:
            author, user_name, category, expert_pk, first_name, last_name, cnt = knowledge_data.values()
            author_pk = expert_pk if not author else author
            name = f'{first_name} {last_name}' if not user_name else user_name
            if author_pk in candidates.keys():
                candidate_data = candidates[author_pk]['categories']
                if category in candidate_data.keys():
                    candidate_data[category] += cnt
                else:
                    candidate_data[category] = cnt
                continue
            candidates[author_pk] = dict(name=name, categories={category: cnt})

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
                candidate_categories[cat.pk] += 1
            else:
                candidate_categories[cat.pk] = 1

        candidates = self._selection_of_candidates(min_count_to_transition, candidates)
        return candidates
