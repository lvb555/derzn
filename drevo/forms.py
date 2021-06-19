from django import forms
from .models import Znanie, Author
from ckeditor.widgets import CKEditorWidget


class ZnanieForm(forms.ModelForm):
    """
    Форма для вывода сущности Знания.
    """
    name = forms.CharField(widget=forms.Textarea(attrs={'cols': 40,
                                                        'rows': 3,
                                                        }
                                                 ),
                           label='Тема'
                           )
    content = forms.CharField(widget=CKEditorWidget(attrs={'cols': 40,
                                                           'rows': 10,
                                                           }
                                                    ),
                              label='Содержание',
                              required=False
                              )

    class Meta:
        model = Znanie
        fields = '__all__'


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
