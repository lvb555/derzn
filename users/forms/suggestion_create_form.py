from django import forms
from drevo.models import Tz, Tr
from django.core.exceptions import ValidationError

def types_validator(value):
    if value is None:
        raise ValidationError('Не все поля заполнены')

class SuggestionCreateForm(forms.Form):
    select_widget = forms.Select(attrs={'class': 'form-control'})
    text_widget = forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Введите название вашего знания'})

    parent_knowledge = forms.CharField(
        max_length=100,
        widget=forms.HiddenInput())
    knowledge_type = forms.ModelChoiceField(
        queryset=Tz.objects.filter(is_systemic=False), 
        label='Тип знания',
        empty_label='Выберите тип знания',
        widget=select_widget, 
        validators=[types_validator])
    relation_type = forms.ModelChoiceField(
        queryset=Tr.objects.filter(is_systemic=False), 
        label='Отношение к старшему знанию', 
        empty_label='Укажите отношение к родительскому знанию',
        widget=select_widget, 
        validators=[types_validator])
    name = forms.CharField(max_length=255, 
        label='Текст знания', 
        widget=text_widget)