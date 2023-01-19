from django import forms
from django.core.exceptions import ValidationError
from ..models import (Znanie,
                      Category
                      )
from ..models.knowledge_kind import Tz
from ckeditor.widgets import CKEditorWidget
from mptt.forms import TreeNodeChoiceField
from ..models.utils import get_model_or_stub


class ZnanieValidators():
    """Валидаторы полей author и href"""
    
    def clean_author(self):
        kind = self.cleaned_data['tz']
        author = self.cleaned_data['author']
        current_tz = Tz.objects.filter(id=kind.id).first()
        if current_tz and current_tz.is_author_required and not author:
            raise ValidationError('Для записей данного вида знаний поле "Автор" является обязательным!')    

        return author
    
    def clean_href(self):
        kind = self.cleaned_data['tz']
        href = self.cleaned_data['href']
        current_tz = Tz.objects.filter(id=kind.id).first()
        if current_tz and current_tz.is_href_required and not href:
            raise ValidationError('Для записей данного вида знаний поле "Источник" является обязательным!')

        return href


class ZnanieForm(forms.ModelForm, ZnanieValidators):
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

