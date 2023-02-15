from django.template import Library

register = Library()


@register.filter
def get_category_count(data: dict, category_pk: int) -> int:
    return data.get(category_pk)
