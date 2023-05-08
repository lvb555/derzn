from django import forms
from mptt.forms import TreeNodeChoiceField
from drevo.models import Znanie, Author, Tz, Tr, Label


class AdvanceTreeSearchFrom(forms.Form):
    """
        Форма расширенного поиска по дереву
    """
    knowledge_type = forms.ModelChoiceField(
        label='Вид знания',
        queryset=Tz.objects.filter(is_systemic=False),
        widget=forms.Select(attrs={'class': 'form-control advanced-search-form'}),
        required=False,
        empty_label='Все'
    )
    author = forms.ModelChoiceField(
        label='Автор',
        queryset=Author.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control advanced-search-form'}),
        required=False,
        empty_label='Все'
    )
    relation_type = forms.ModelChoiceField(
        label='Вид связи',
        queryset=Tr.objects.filter(is_systemic=False),
        widget=forms.Select(attrs={'class': 'form-control advanced-search-form'}),
        required=False,
        empty_label='Все'
    )
    tag = forms.ModelMultipleChoiceField(
        label='Тег',
        queryset=Label.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control advanced-search-form-multiple scrollbar'}),
        required=False,
        help_text='Выбор нескольких тегов проводится при нажатой клавише CTRL'
    )

