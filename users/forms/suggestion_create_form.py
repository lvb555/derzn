from django import forms
from drevo.models import Tz, Tr
from django.core.exceptions import ValidationError

tz = [(i.id, i.name) for i in Tz.objects.filter(is_systemic=False)]
tr = [(i.id, i.name) for i in Tr.objects.filter(is_systemic=False)]

tz = tuple([(-1, 'Выберите подходящий тип знания')] + tz)
tr = tuple([(-1, 'Укажите отношение к текущему знанию')] + tr)

def types_validator(value):
    if int(value) == -1:
        raise ValidationError('Не все поля заполнены')

class SuggestionCreateForm(forms.Form):
    select_widget = forms.Select(attrs={'class': 'form-control'})
    text_widget = forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Введите название вашего знания'})

    parent_knowledge = forms.CharField(max_length=100, widget=forms.HiddenInput())
    knowledge_type = forms.ChoiceField(choices=tz, label='Тип знания', widget=select_widget, validators=[types_validator])
    relation_type = forms.ChoiceField(choices=tr, label='Отношение к старшему знанию', widget=select_widget, validators=[types_validator])
    name = forms.CharField(max_length=256, label='Текст знания', widget=text_widget)