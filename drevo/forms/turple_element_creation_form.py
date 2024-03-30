from django import forms
from drevo.models import TurpleElement


class TurpleElementForm(forms.ModelForm):
    class Meta:
        model = TurpleElement
        fields = ['value', 'weight']
