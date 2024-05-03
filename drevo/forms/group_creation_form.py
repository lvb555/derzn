from django import forms
from mptt.forms import TreeNodeChoiceField
from drevo.models import TemplateObject, Znanie


class GroupForm(forms.Form):
    name = forms.CharField(max_length=255, label='Имя')
    parent = TreeNodeChoiceField(queryset=TemplateObject.objects.all(), label='Родитель', empty_label='Без родителя')
    knowledge = forms.ModelChoiceField(queryset=Znanie.objects.all(), widget=forms.HiddenInput)
