from django import template
from django.utils.safestring import mark_safe

from drevo.models.knowledge_grade_scale import KnowledgeGradeScale
from drevo.models.relation import Relation
from drevo.utils import get_average_proof_base_and_common_grades, get_group_users

register = template.Library()


@register.filter
def object_grade(obj, user):
    """Возвращает оценку (грейд) Знания или Связи от пользователя.
    Если ее нет - возвращает оценку по умолчанию для объекта"""
    grade = obj.grades.filter(user=user).first()
    if grade:
        return grade.grade
    else:
        return obj.get_default_grade()


@register.filter
def object_grade_num(obj, user):
    """Возвращает численную оценку от пользователя. Если ее нет - возвращает значение по умолчанию"""
    grade = object_grade(obj, user)

    # чтобы не показывать оценку знания для значения по умолчанию и 0
    if isinstance(grade, KnowledgeGradeScale) and (grade.is_hidden() or grade.get_base_grade() == 0):
        return None

    return object_grade(obj, user).get_base_grade()


@register.filter
def multiply(a, b):
    if a and b:
        return float(a) * float(b)
    return KnowledgeGradeScale.objects.all().first().get_base_grade()


@register.filter
def grade_name(value):
    """ " Возвращаем название оценки Знания для значения оценки value
    для None вернет оценку по умолчанию
    """
    return KnowledgeGradeScale.get_grade_object(value).name


@register.filter
def common_grades(knowledge, request):
    return knowledge.get_common_grades(request)[0]


@register.filter
def group_common_grades(knowledge, request):
    users = get_group_users(request, knowledge.id)
    return get_average_proof_base_and_common_grades(users, request, knowledge)


@register.filter
def proof_weight(relation: Relation, request):
    variant = request.GET.get("variant")
    if variant and variant.isdigit():
        variant = int(variant)
    else:
        variant = 1

    return relation.get_proof_weight(request, variant)


@register.filter
def proof_grade(relation: Relation, request):
    variant = request.GET.get("variant")
    if variant and variant.isdigit():
        variant = int(variant)
    else:
        variant = 1

    return relation.get_proof_grade(request, variant)


@register.filter
def grade(value):
    obj = KnowledgeGradeScale.get_grade_object(value)
    return obj


@register.simple_tag()
def scale_color_styles():
    """
    Функция для формирования набора стилей для шкалы знаний
    <style>
        .scale_{grade.pk}_positive {background-color: xxx; color: xxx;}
        .scale_{grade.pk}_negative {background-color: xxx; color: xxx;}
    </style>
    """

    result = ["<style>"]
    for grade in KnowledgeGradeScale.get_cache():
        result.append(
            f".scale_{grade.pk}_positive {{"
            f"background: {grade.argument_color_background}; "
            f"background-color: {grade.argument_color_background}; "
            f"color: {grade.argument_color_font};}}"
        )

        result.append(
            f".scale_{grade.pk}_negative {{"
            f"background: {grade.argument_color_background}; "
            f"background-color: {grade.contraargument_color_background}; "
            f"color: {grade.contraargument_color_font};}}"
        )

    result.append("</style>")
    return mark_safe("\n".join(result))


@register.filter
def get_color_style(grade: KnowledgeGradeScale | int, is_positive=True):
    """Возвращает название стиля для значения шкалы grade
    По умолчанию возвращает стиль для положительного (аргумент) значения
    """
    if grade is None:
        pk = KnowledgeGradeScale.get_default_grade().pk
    elif isinstance(grade, KnowledgeGradeScale):
        pk = grade.pk
    else:
        pk = grade

    if not is_positive:
        return f"scale_{pk}_negative"
    else:
        return f"scale_{pk}_positive"


@register.simple_tag
def define(val=None):
    return val
