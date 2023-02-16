from drevo.utils import get_elements_tree, get_group_users, get_color_from_hsl
from drevo.models.knowledge import Znanie
from drevo.models.knowledge_grade_color import KnowledgeGradeColor
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

@register.simple_tag
def get_gradients():
    """
    Функция для формирования двух спектров (любая оценка, довод против)
    """
    bg_color = {
        "for": {
            "low_light": get_color_from_hsl(0, 1),
            "high_light": get_color_from_hsl(0, 0),
        },
        "against": {
            "low_light": get_color_from_hsl(1, 1),
            "high_light": get_color_from_hsl(1, 0),
        }
    }
    return bg_color

@register.filter
def get_color_from_knowledge_grade_value(value: float, knowledge_type: bool):
    """
    Функция для формирования цвета в формате hsl для знания
    """
    range_color = KnowledgeGradeColor.objects.get(
        knowledge_type=knowledge_type)
    saturation = (range_color.saturation*100)/255
    light = 100 - ((
        (range_color.high_light - range_color.low_light) \
        * value + range_color.low_light) * 100) / 255
    color = f"hsl({range_color.hue}, {saturation}%, {light}%)"
    return color
