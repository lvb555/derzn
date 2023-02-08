from ..models import InterviewAnswerExpertProposal
from django.template import Library

register = Library()


@register.filter()
def get_norm_status_value(raw_value: str) -> str:
    return {
        key: f'{value}о' if value in ('Принят', 'Не принят') else value
        for key, value in InterviewAnswerExpertProposal.STATUSES
    }.get(raw_value)
