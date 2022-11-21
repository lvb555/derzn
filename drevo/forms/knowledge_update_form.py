from ckeditor.widgets import CKEditorWidget
from django import forms
from django.forms import inlineformset_factory, BaseInlineFormSet
from mptt.forms import TreeNodeChoiceField

from drevo.common import variables
from drevo.models import Category, Label, Znanie, ZnImage
from drevo.models.utils import get_model_or_stub


class ZnanieUpdateForm(forms.ModelForm):
    """Форма редактирования знания"""
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
    labels = forms.ModelMultipleChoiceField(queryset=Label.objects.all(), label='Метки', required=False)

    class Meta:
        model = Znanie
        exclude = ('id', 'date', 'updated_at', 'user', 'expert', 'redactor', 'director', 'is_published')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name != 'is_send':
                field.widget.attrs['class'] = 'form-control'
            if self.instance.get_current_status.status not in variables.EDIT_STATUS:
                field.widget.attrs['readonly'] = True


class ImageFormSet(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ImageFormSet, self).__init__(*args, **kwargs)
        try:
            if self.instance.znanie.get_current_status.status not in variables.EDIT_STATUS:
                for field_name, field in self.fields.items():
                    field.widget.attrs['hidden'] = True
        except Exception as err:
            pass


ZnImageEditFormSet = inlineformset_factory(
    Znanie,
    ZnImage,
    form=ImageFormSet,
    fields=('photo',),
    extra=1,
    can_delete=False
)
