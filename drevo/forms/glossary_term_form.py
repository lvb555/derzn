from django import forms
from ..models import Znanie

from ckeditor.widgets import CKEditorWidget
from mptt.forms import TreeNodeChoiceField


class GlossaryTermForm(forms.ModelForm):
    """
    Форма для вывода терминов глоссария.
    """
    description = forms.CharField(widget=CKEditorWidget(attrs={'cols': 40,
                                                               'rows': 10,
                                                               }
                                                        ),
                                  label='Описание',
                                  required=False
                                  )

    class Meta:
        model = Znanie
        fields = '__all__'
