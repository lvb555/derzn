from drevo.models.knowledge import Znanie
from django import template

register = template.Library()


@register.filter
def has_children(knowledge: Znanie) -> bool:
    """
    Функция для проверки есть ли у данного знания свое знание его доказательной
    базы
    """
    relations = knowledge.base.filter(
        tr__is_argument=True,
        rz__tz__can_be_rated=True,
    )
    return bool(relations)
