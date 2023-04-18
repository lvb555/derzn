from django import forms
from drevo.models import Znanie


class AdditionalKnowledgeForm(forms.ModelForm):
    """
        Форма для дополнительных связей
    """
    class Meta:
        model = Znanie
        fields = ('name', 'tz', 'content', 'href', 'source_com', 'labels')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'tz': forms.Select(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control'}),
            'href': forms.TextInput(attrs={'class': 'form-control'}),
            'source_com': forms.TextInput(attrs={'class': 'form-control'}),
            'labels': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }
