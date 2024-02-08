from django import forms
from drevo.models import Var, TurpleElement


class TurpleElementForm(forms.ModelForm):
    class Meta:
        model = TurpleElement
        fields = ['value', 'var', 'weight',]
