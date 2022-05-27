from django import template

register = template.Library()


@register.filter
def endings_filter(word: str, plural=False) -> str:
    """
    Хуманизация согласно дополнению для issue 78
    для слов в единственном и множественном числе.

    На вход подается строка с окончаниями в квадратных скобках.
    Например, "Исключени [е, я]".
    Если в скобках указано одно окончание, оно не присоединяется.
    Если окончаний несколько, при plural=False присоединяет первое из списка,
    иначе - второе.

    Описание:
    https://github.com/breduin/derzn/issues/78#issuecomment-1114019674
    """

    first = '['
    last = ']'
    sep = ', '

    if first in word and last in word:
        first_index = word.index(first)
        last_index = word.index(last)

        if first_index and last_index and first_index < last_index:
            main_word = word.split(' ')[0]
            tail = word.split(first)[-1].replace(last, '')
            if tail:
                endings = tail.split(sep)
                if any(endings):
                    if len(endings) == 2:
                        if plural:
                            return f'{main_word}{endings[1]}'
                        else:
                            return f'{main_word}{endings[0]}'

            return main_word

    return word
