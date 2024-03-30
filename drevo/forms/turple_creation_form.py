from django import forms
from drevo.models import Znanie
from drevo.models import Turple


class TurpleForm(forms.ModelForm):
    class Meta:
        model = Turple
        fields = ['name', 'weight']