from django import template
from drevo.utils import get_average_proof_base_and_common_grades, get_group_users
from drevo.models.knowledge_grade_scale import KnowledgeGradeScale
from drevo.models.relation import Relation

register = template.Library()


@register.filter
def object_grade(obj, user):
    grade = None
    grades = obj.grades.filter(user=user)
    if grades.exists:
        grade = grades.first().grade
    return grade


@register.filter
def object_grade_num(obj, user):
    grades = obj.grades.filter(user=user)
    if grades.exists():
        grade = grades.first().grade.get_base_grade()
    else:
        grade = f'{obj.get_default_grade()}'
    return grade


@register.filter
def multiply(a, b):
    if a and b:
        return float(a) * float(b)
    return KnowledgeGradeScale.objects.all().first().get_base_grade()


@register.filter
def grade_name(value):
    obj = KnowledgeGradeScale.get_grade_object(value)
    if obj:
        return obj.name
    return ''


@register.filter
def common_grades(knowledge, request):
    return knowledge.get_common_grades(request)

@register.filter
def group_common_grades(knowledge, request):
    users = get_group_users(request, knowledge.id)
    return get_average_proof_base_and_common_grades(users, request, knowledge)

@register.filter
def proof_weight(relation: Relation, request):
    variant = request.GET.get('variant')
    if variant and variant.isdigit():
        variant = int(variant)
    else:
        variant = 1

    return relation.get_proof_weight(request, variant)

@register.filter
def proof_grade(relation: Relation, request):
    variant = request.GET.get('variant')
    if variant and variant.isdigit():
        variant = int(variant)
    else:
        variant = 1

    return relation.get_proof_grade(request, variant)

@register.filter
def grade(value):
    obj = KnowledgeGradeScale.get_grade_object(value)
    return obj
