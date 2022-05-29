from django import template
from drevo.models.knowledge_grade_scale import KnowledgeGradeScale

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
