from django import forms
from django.core.exceptions import ValidationError
from ..models import (Znanie,
                      Category,
                      knowledge_kind
                      )
from ckeditor.widgets import CKEditorWidget
from mptt.forms import TreeNodeChoiceField
from ..models.utils import get_model_or_stub



class MyValidators():
    
    def clean_author(self):
        kind = self.cleaned_data['tz']
        author = self.cleaned_data['author']
        try:
            is_author_required = knowledge_kind.objects.get(id=kind.id).is_author_required
            if is_author_required and author == None:
                raise ValidationError('Для данного вида знаний поле автор является обязательным!')
        except AttributeError:
            print('Необходимо указать вид знания')

        return author
    
    def clean_href(self):
        kind = self.cleaned_data['tz']
        href = self.cleaned_data['href']
        try:
            is_author_required = knowledge_kind.objects.get(id=kind.id).is_href_required
            if is_author_required and href == None:
                raise ValidationError('Для данного вида знаний поле источник является обязательным!')
        except AttributeError:
            print('Необходимо указать вид знания')

        return href


class ZnanieForm(forms.ModelForm, MyValidators):
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
