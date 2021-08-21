from django import template

register = template.Library()

@register.filter
def dict_value(d, key):
    return d[key]
