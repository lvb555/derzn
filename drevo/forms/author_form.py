from django import forms
from ..models import Author
from ckeditor.widgets import CKEditorWidget


class AuthorForm(forms.ModelForm):
    """
    Форма для вывода сущности Author.
    """
    info = forms.CharField(widget=CKEditorWidget(attrs={'cols': 40,
                                                        'rows': 10,
                                                        }
                                                 ),
                           label='Сведения об авторе',
                           required=False
                           )

    class Meta:
        model = Author
        fields = '__all__'
