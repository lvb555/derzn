"""
Фильтр для шаблона, возвращает значение словаря по ключу из текущей переменно,
см. описание http://userone.ru/?q=node/30
"""
from django import template

register = template.Library()


@register.filter
def dict_value(d, key):
    return d.get(key)
