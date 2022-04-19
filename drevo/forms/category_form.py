from django import forms
from ..models import Category
from ckeditor.widgets import CKEditorWidget


class CategoryForm(forms.ModelForm):
    """
    Форма для вывода сущности Category.
    """
    content = forms.CharField(widget=CKEditorWidget(attrs={'cols': 40,
                                                           'rows': 10,
                                                           }
                                                    ),
                              label='Содержание',
                              required=False
                              )

    class Meta:
        model = Category
        exclude = ('visits',)
