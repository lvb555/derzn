from functools import reduce
from operator import or_

from django.db.models import Q
from drevo.models import Znanie, Relation, SpecialPermissions, Category, RelationStatuses


class PreparingRelationsMixin:
    """
        Миксин для подготовки связей
    """
    def get_queryset(self, user, stage: str, status: str = None):
        methods_data = {
            'create': self.__get_create_queryset,
            'update': self.__get_update_queryset,
            'expertise': self.__get_expertise_queryset,
            'publication': self.__get_publication_queryset
        }
        return methods_data.get(stage)(user=user, status=status)

    @staticmethod
    def __get_create_queryset(user, status: str = None):
        return (
                Znanie.objects
                .filter(
                    (
                        Q(is_published=True)
                        # (Q(knowledge_status__status='PUB_PRE') | Q(knowledge_status__status='PUB'))
                        # & Q(knowledge_status__is_active=True)
                    )
                    | Q(user=user)
                )
            )

    @staticmethod
    def __get_update_queryset(user, status: str = None):
        statuses = {
            'user': ('WORK_PRE', 'PRE_FIN'),
            'expert': ('WORK', 'FIN')
        }

        user_role = 'expert' if user.is_expert else 'user'
        filter_data = (status,) if status else statuses.get(user_role)

        return (
                Znanie.objects
                .filter(
                    (
                        (
                            Q(base__relation_status__status__in=filter_data)
                            & Q(base__relation_status__is_active=True)
                        )
                        |
                        (
                            Q(related__relation_status__status__in=filter_data)
                            & Q(related__relation_status__is_active=True)
                        )
                    )
                    & Q(related__user=user)
                )
            )

    def __get_category_for_knowledge(self, knowledge: Znanie) -> [None, Category]:
        if knowledge.category and knowledge.category.is_published and knowledge.is_published:
            return knowledge.category
        if not knowledge.is_published:
            return None
        if relation := Relation.objects.filter(rz=knowledge).first():
            base_knowledge = relation.bz
            return self.__get_category_for_knowledge(base_knowledge)
        return None

    def _get_additional_knowledge(self, knowledge, competence) -> list:
        """
            Метод для получения категорий для дополнительных знаний (знаний без категорий)
            Результирующие  данные: \n
            [knowledge_pk1, knowledge_pk2...]
        """
        without_cat_data = list()
        for kn_obj in knowledge:
            if kn_obj.category:
                continue
            category = self.__get_category_for_knowledge(kn_obj)
            if category in competence:
                without_cat_data.append(kn_obj.pk)
        return without_cat_data

    def __get_knowledge_by_competence(self, user, role, base_lookups):
        user_competencies = SpecialPermissions.objects.filter(expert=user).first()
        if not user_competencies:
            return
        user_competencies = (
            user_competencies.categories.all() if role == 'expert' else user_competencies.admin_competencies.all()
        )
        queryset = Znanie.objects.select_related('category').filter(base_lookups)
        knowledge_list = list()
        knowledge_without_cat = list()
        for know in queryset:
            if know.category in user_competencies:
                knowledge_list.append(know.pk)
            else:
                knowledge_without_cat.append(know)

        knowledge_without_cat = self._get_additional_knowledge(knowledge_without_cat, user_competencies)
        required_kn = knowledge_list + [kn_id for kn_id in knowledge_without_cat]
        return queryset.filter(pk__in=required_kn).distinct()

    def __get_expertise_queryset(self, user, status: str = None):
        statuses = ('PRE_EXP', 'PRE_READY', 'PRE_FIN', 'PRE_REJ')
        statuses_data = {'my': ('PRE_EXP', 'PRE_FIN'), 'competence': ('PRE_READY', 'PRE_REJ')}

        if not status:
            user_competencies = SpecialPermissions.objects.filter(expert=user).first()
            if not user_competencies:
                return
            user_competencies = user_competencies.categories.all()
            queryset = (
                Znanie.objects.select_related('category')
                .filter(
                    (Q(base__relation_status__status__in=statuses) & Q(base__relation_status__is_active=True))
                    | (Q(related__relation_status__status__in=statuses) & Q(related__relation_status__is_active=True))
                )
            )
            knowledge_list = list()
            knowledge_without_cat = list()
            for know in queryset:
                if know.category in user_competencies:
                    knowledge_list.append(know.pk)
                else:
                    knowledge_without_cat.append(know)

            knowledge_without_cat = self._get_additional_knowledge(knowledge_without_cat, user_competencies)
            required_kn = knowledge_list + [kn_id for kn_id in knowledge_without_cat]
            return (
                queryset
                .filter(
                    (Q(related__relation_status__status__in=statuses_data.get('my')) & Q(related__expert=user))
                    |
                    (Q(related__relation_status__status__in=statuses_data.get('competence')) & Q(pk__in=required_kn))
                )
                .distinct()
            )

        for category, statuses in statuses_data.items():
            if status not in statuses:
                continue
            base_lookups = (Q(related__relation_status__status=status) & Q(related__relation_status__is_active=True))
            if category == 'my':
                filter_lookups = base_lookups & (Q(related__expert=user))
                return Znanie.objects.filter(filter_lookups)
            else:
                return self.__get_knowledge_by_competence(user, 'expert', base_lookups)

    def __get_publication_queryset(self, user, status: str = None):
        statuses_data = ('PRE_FIN', 'PUB_PRE', 'PRE_REJ', 'FIN', 'PUB', 'REJ')
        statuses = (status,) if status else statuses_data
        base_lookups = reduce(
            or_, [
                (Q(base__relation_status__status__in=statuses) & Q(base__relation_status__is_active=True)),
                (Q(related__relation_status__status__in=statuses) & Q(related__relation_status__is_active=True))
            ]
        )
        return self.__get_knowledge_by_competence(user, 'director', base_lookups)

    @staticmethod
    def get_norm_stage_name(system_name: str) -> str:
        stage_names = {
            'WORK_PRE': 'ПредСвязь в работе',
            'WORK': 'Связь в работе',
            'PRE_READY': 'Готовая ПредСвязь',
            'PRE_FIN': 'Завершенная ПредСвязь',
            'FIN': 'Завершенная Связь',
            'PRE_EXP': 'Экспертизв ПредСвязи',
            'REJ': 'Отклоненная Связь',
            'PRE_REJ': 'Отклоненная ПредСвязь',
            'PUB_PRE': 'Опубликованная ПредСвязь',
            'PUB': 'Опубликованная Связь'
        }
        return stage_names.get(system_name)

    @staticmethod
    def get_relation_update_context(bz_pk: int, rz_pk: int):
        context = dict()
        relation = Relation.objects.select_related('bz', 'rz').filter(bz_id=bz_pk, rz_id=rz_pk).first()
        cur_status = RelationStatuses.objects.filter(relation=relation, is_active=True).first()
        context['cur_status'] = cur_status.status
        context['relation'] = relation
        return context

    @staticmethod
    def is_readonly_status(status: str, stage: str) -> bool:
        statuses_by_stage = {
            'update': ('PRE_READY', 'FIN',),
            'expertise': ('PRE_REJ', 'PRE_FIN',),
            'publication': ('PUB_PRE', 'PUB',)
        }
        return True if status in statuses_by_stage.get(stage) else False
