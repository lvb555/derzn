"""
Возвращает из списка значение по индексу
например list|index:1
"""
from django import template

register = template.Library()


# тег для получения элемента списка
@register.filter
def index(indexable, i):
    return indexable[i]
