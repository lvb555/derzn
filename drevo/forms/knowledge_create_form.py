from ckeditor.widgets import CKEditorWidget
from django import forms
from django.db.models import Q
from django.forms import inlineformset_factory
from mptt.forms import TreeNodeChoiceField
from drevo.models import Znanie, Category, ZnImage, Label, Tz, ZnFile
from drevo.models.utils import get_model_or_stub

from .knowledge_form import ZnanieValidators


class ZnanieCreateForm(forms.ModelForm, ZnanieValidators):
    """
    Форма создания сущности Знание
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

    category = TreeNodeChoiceField(queryset=get_model_or_stub(Category).published.all(),
                                   empty_label="(нет категории)",
                                   label='Категория',
                                   required=True)
    labels = forms.ModelMultipleChoiceField(queryset=Label.objects.all(), label='Метки', required=False)
    tz = forms.ModelChoiceField(queryset=Tz.objects.all().order_by('name'), label='Вид знания')

    class Meta:
        model = Znanie
        exclude = ('id', 'date', 'updated_at', 'user', 'expert', 'redactor', 'director', 'is_published', 'meta_info')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name != 'is_send' and not isinstance(field, forms.BooleanField):
                field.widget.attrs['class'] = 'form-control'


ZnImageFormSet = inlineformset_factory(
    Znanie,
    ZnImage,
    fields=('photo',),
    extra=3,
    can_delete=False
)


ZnFilesFormSet = inlineformset_factory(
    Znanie,
    ZnFile,
    fields=('file',),
    extra=1,
    can_delete=False
)
