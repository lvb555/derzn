from django import forms
from mptt.forms import TreeNodeChoiceField
from drevo.models import Znanie, Author, Category, Tz, Tr, Label


class AdvanceTreeSearchFrom(forms.Form):
    """
        Форма расширенного поиска по дереву
    """
    knowledge_type = forms.ModelChoiceField(
        label='Вид знания',
        queryset=Tz.objects.filter(is_systemic=False),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    category = TreeNodeChoiceField(
        label='Категория',
        queryset=Category.tree_objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    author = forms.ModelChoiceField(
        label='Автор',
        queryset=Author.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    relation_type = forms.ModelChoiceField(
        label='Вид связи',
        queryset=Tr.objects.filter(is_systemic=False),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    tag = forms.ModelMultipleChoiceField(
        label='Тег',
        queryset=Label.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        help_text='Чтобы выделить несколько тегов выберите их предварительно зажав "CTRL"'
    )

