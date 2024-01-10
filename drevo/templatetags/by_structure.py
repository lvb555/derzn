from django import template

register = template.Library()

@register.filter
def by_structure(value, arg):
    return value.filter(structure=arg)
