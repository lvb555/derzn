"""
Реализует изменение окончания
"""
from django import template

register = template.Library()


@register.filter
def ending(text: str, type_text: str):
    text = str(text)
    if all(((i in text) for i in '[]')):
        i_start = text.rfind('[')
        i_end = text.rfind(']')

        endings = text[i_start + 1:i_end].split(',')
        if endings:
            text_ending = ''
            if type_text == 'plural':
                text_ending = endings[-1].strip()
            elif type_text == 'singular' and len(endings) == 2:
                text_ending = endings[0].strip()

            text = ' '.join(map(lambda part: part.strip(), [text[:i_start].strip() + text_ending, text[i_end + 1:]]))
    return text
