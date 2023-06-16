from ckeditor.widgets import CKEditorWidget
from django import forms
from django.forms import inlineformset_factory
from drevo.models import Znanie, ZnImage


class AdditionalKnowledgeForm(forms.ModelForm):
    """
        Форма для дополнительных связей
    """
    content = forms.CharField(widget=CKEditorWidget(), label='Содержание', required=False)

    def __init__(self, *args, **kwargs):
        super(AdditionalKnowledgeForm, self).__init__(*args, **kwargs)
        for _, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = Znanie
        fields = ('name', 'tz', 'content', 'href', 'source_com', 'labels')


ZnImageFormSet = inlineformset_factory(
    Znanie,
    ZnImage,
    fields=('photo',),
    extra=3,
    can_delete=False
)
