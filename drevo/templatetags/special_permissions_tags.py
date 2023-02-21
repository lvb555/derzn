from django.template import Library

register = Library()


@register.filter
def get_category_count(data: dict, category_pk: int) -> int:
    return data.get(category_pk)


@register.filter
def knowledge_count_by_competencies(competencies_data: dict, competencies_pk: int) -> int:
    return competencies_data.get(competencies_pk).get('knowledge_count')


@register.filter
def expertise_count_by_competencies(competencies_data: dict, competencies_pk: int) -> int:
    return competencies_data.get(competencies_pk).get('expertise_count')


@register.filter
def preknowledge_count_by_competencies(competencies_data: dict, competencies_pk: int) -> int:
    return competencies_data.get(competencies_pk).get('preknowledge_count')
