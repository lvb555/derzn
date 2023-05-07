from ckeditor.widgets import CKEditorWidget
from django import forms
from django.forms import inlineformset_factory, BaseInlineFormSet
from mptt.forms import TreeNodeChoiceField

from drevo.common import variables
from drevo.models import Category, Label, Znanie, ZnImage, Tz
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


class TableUpdateForm(ZnanieUpdateForm):
    """Форма создания Знания вида Таблица"""
    try:
        tz_id = Tz.objects.get(name='Таблица').id
    except Tz.DoesNotExist:
        pass

    @staticmethod
    def special_permissions_for_expert(user=None):
        """Выбор всех категорий в компетенции эксперта"""
        _categories = Category.tree_objects.exclude(is_published=False)
        result_categories = []
        for category in _categories:
            if user:
                experts = category.get_expert_ancestors_category()
                if user in experts:
                    result_categories.append(category)
            else:
                result_categories.append(category)

        return result_categories

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Присвоение вида знания "Таблица"
        self.fields['tz'].initial = Tz.objects.get(name='Таблица')
        self.fields['tz'].widget = forms.HiddenInput()

        # Выбор всех категорий в компетенции конкретного пользователя
        categories = self.special_permissions_for_expert(user)
        queryset = get_model_or_stub(Category).objects.filter(pk__in=[category.pk for category in categories])

        # Категории в компетенциях конкретного эксперта
        self.fields['category'] = TreeNodeChoiceField(queryset=queryset,
                                                      empty_label='Выберите категорию',
                                                      label='Категория',
                                                      required=True)
