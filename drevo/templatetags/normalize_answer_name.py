import textwrap
from django.template import Library

register = Library()


@register.filter(name='normalize_answer_name')
def normalize_answer_name(answer_name):
    if len(answer_name) > 35:
        return '\n'.join(textwrap.wrap(answer_name, 35))
    return answer_name
