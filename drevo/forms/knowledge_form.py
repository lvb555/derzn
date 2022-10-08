from django import forms
from ..models import (Znanie,
                      Category,
                      )
from ckeditor.widgets import CKEditorWidget
from mptt.forms import TreeNodeChoiceField
from ..models.utils import get_model_or_stub


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

    category = TreeNodeChoiceField(queryset=get_model_or_stub(Category).tree_objects.all(),
                                   empty_label="(нет категории)",
                                   label='Категория',
                                   required=False)

    class Meta:
        model = Znanie
        fields = '__all__'

    class Meta:
        model = Znanie
        fields = '__all__'