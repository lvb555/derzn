from django import forms
from ..models.chapter import ChapterDescriptions
from ckeditor.widgets import CKEditorWidget


class ChapterForm(forms.ModelForm):
    """
    Форма для вывода модели "Глава описания".
    """
    content = forms.CharField(widget=CKEditorWidget(attrs={'cols': 40,
                                                           'rows': 10,
                                                           }
                                                    ),
                              label='Содержание',
                              required=False
                              )

    class Meta:
        model = ChapterDescriptions
        fields = '__all__'
