from ..models import InterviewAnswerExpertProposal, Znanie, SpecialPermissions
from django.template import Library

register = Library()


@register.filter()
def get_norm_status_value(raw_value: str) -> str:
    return {
        key: f'{value}о' if value in ('Принят', 'Не принят') else value
        for key, value in InterviewAnswerExpertProposal.STATUSES
    }.get(raw_value)

@register.simple_tag
def get_interview_in_categories(expert):
    categories = SpecialPermissions.objects.filter(expert=expert).values_list('categories__name')
    interview = Znanie.objects.filter(tz__name='Интервью', category__name__in=categories)\
        .values_list('category__name',flat=True).distinct()
    return interview
