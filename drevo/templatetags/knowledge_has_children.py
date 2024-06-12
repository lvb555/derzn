from django import template

from drevo.models.knowledge import Znanie

register = template.Library()


@register.filter
def has_children(knowledge: Znanie) -> bool:
    """
    Функция для проверки есть ли у данного знания свое знание его доказательной
    базы
    """
    return knowledge.base.filter(
        tr__is_argument=True,
        rz__tz__can_be_rated=True,
    ).exists()
