from django.db.models import Q
from drevo.models import Znanie, Relation


class PreparingRelationsMixin:
    """
        Миксин для подготовки связей
    """
    def get_queryset(self, user, stage: str, status: str = None):
        if stage == 'create':
            return (
                Znanie.objects
                .filter(
                    Q(base__is_published=True) | Q(related__is_published=True)
                    | (Q(user=user) | Q(expert=user) | Q(director=user))
                )
            )
        filter_data = (status,) if not status else self.get_related_relation_statuses(stage_name=stage)
        return #Znanie.objects.filter(relation__relation_status__in=filter_data)

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
    def get_related_relation_statuses(stage_name: str) -> tuple:
        statuses = {
            'update': ('WORK_PRE', 'PRE_FIN', 'WORK', 'FIN'),
            'expertise': ('PRE_FIN', 'PRE_EXP', 'PRE_REJ', 'PRE_READY'),
            'publication': ('PRE_FIN', 'PUB_PRE', 'PRE_REJ', 'FIN', 'PUB', 'REJ')
        }
        return statuses.get(stage_name)
