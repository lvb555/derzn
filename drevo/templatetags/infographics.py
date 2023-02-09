from drevo.utils import get_elements_tree, get_group_users
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
    return get_elements_tree(
        index_element_tree, request, proof_relations)

@register.filter
def elements_tree_group_knowledge(knowledge: Znanie, request):
    """
    Функция для отрисовки инфографики
    """
    proof_relations = knowledge.base.filter(
        tr__is_argument=True,
        rz__tz__can_be_rated=True,
    ).order_by('tr__name')

    index_element_tree = 0
    users = get_group_users(request, knowledge.id)
    return get_elements_tree(
        index_element_tree, request, proof_relations,
        is_group_knowledge=True, users=users)
