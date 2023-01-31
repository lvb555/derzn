from drevo.utils import get_elements_tree
from drevo.models.knowledge import Znanie
from django import template

register = template.Library()


@register.filter
def elements_tree(knowledge: Znanie, request):
    """
    Функция для отрисовки инфографики
    """
    proof_relations = knowledge.base.filter(
        tr__is_argument=True,
        rz__tz__can_be_rated=True,
    ).order_by('tr__name')

    index_element_tree = 0
    elements_tree = get_elements_tree(
        index_element_tree, request, proof_relations)

    return elements_tree
