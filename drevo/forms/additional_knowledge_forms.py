from django import forms
from drevo.models import Znanie


class AdditionalKnowledgeForm(forms.ModelForm):
    """
        Форма для дополнительных связей
    """
    def __init__(self, *args, **kwargs):
        super(AdditionalKnowledgeForm, self).__init__(*args, **kwargs)
        for _, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = Znanie
        fields = ('name', 'tz', 'content', 'href', 'source_com', 'labels')
