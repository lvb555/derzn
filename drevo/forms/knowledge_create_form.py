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
        exclude = ('id', 'date', 'updated_at', 'user', 'expert', 'redactor', 'director', 'is_published')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name != 'is_send':
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


class RelationCreateForm(forms.ModelForm, ZnanieValidators):
    """Форма создания Знания вида Строка"""
    name = forms.CharField(widget=forms.Textarea(attrs={'cols': 40,
                                                        'rows': 4,
                                                        }
                                                 ),
                           label='Тема'
                           )

    tz = forms.ModelChoiceField(queryset=Tz.objects.filter(Q(name='Заголовок') | Q(name='Группа')).order_by('name'),
                                label='Вид знания',
                                required=True)

    class Meta:
        model = Znanie
        exclude = ('id', 'category', 'content', 'date', 'updated_at', 'user', 'expert', 'redactor', 'director',
                   'is_send', 'is_published', 'labels', 'author', 'href', 'source_com', 'order', 'show_link',
                   'notification')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name != 'is_send':
                field.widget.attrs['class'] = 'form-control'


class QuestionToQuizCreateForm(forms.ModelForm, ZnanieValidators):
    """Форма создания вопроса теста"""
    name = forms.CharField(widget=forms.Textarea(attrs={'cols': 40,
                                                        'rows': 4,
                                                        }
                                                 ),
                           label='Тема'
                           )

    tz = forms.ModelChoiceField(queryset=Tz.objects.filter(Q(name='Вопрос') | Q(name='Вопрос теста')).order_by('name'),
                                label='Вид знания',
                                required=True)

    class Meta:
        model = Znanie
        exclude = ('id', 'category', 'content', 'date', 'updated_at', 'user', 'expert', 'redactor', 'director',
                   'is_send', 'is_published', 'labels', 'author', 'href', 'source_com', 'order', 'show_link',
                   'notification')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name != 'is_send':
                field.widget.attrs['class'] = 'form-control'


class NameOfZnanieCreateUpdateForm(forms.ModelForm, ZnanieValidators):
    """Форма создания и редактирования знания, в которой есть только тема"""
    name = forms.CharField(widget=forms.Textarea(attrs={'cols': 40,
                                                        'rows': 4,
                                                        }
                                                 ),
                           label='Тема'
                           )

    class Meta:
        model = Znanie
        exclude = ('id', 'category', 'content', 'date', 'updated_at', 'user', 'expert', 'redactor', 'director',
                   'is_send', 'is_published', 'labels', 'author', 'href', 'source_com', 'order', 'show_link',
                   'tz', 'notification')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name != 'is_send':
                field.widget.attrs['class'] = 'form-control'


class TableOrQuizCreateEditForm(ZnanieCreateForm):
    """Форма создания и редактирования Знания вида «Таблица» или «Тест»"""

    @staticmethod
    def special_permissions_for_user(type_of_zn, user=None):
        """Выбор всех категорий в компетенции руководителя или эксперта"""
        _categories = Category.tree_objects.exclude(is_published=False)
        result_categories = []
        for category in _categories:
            if user:
                if type_of_zn == 'Таблица':
                    experts = category.get_admin_ancestors_category()
                else:
                    experts = category.get_expert_ancestors_category()
                if user in experts:
                    result_categories.append(category)
            else:
                result_categories.append(category)

        return result_categories

    def __init__(self, user, type_of_zn, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if type_of_zn == 'Таблица':
            # Присвоение виду знания "Таблица"
            self.fields['tz'].initial = Tz.objects.get(name='Таблица')
        else:
            # Присвоение виду знания "Тест"
            self.fields['tz'].initial = Tz.objects.get(name='Тест')

        self.fields['tz'].widget = forms.HiddenInput()

        # Выбор всех категорий в компетенции конкретного пользователя
        categories = self.special_permissions_for_user(type_of_zn, user)
        queryset = get_model_or_stub(Category).objects.filter(pk__in=[category.pk for category in categories])

        self.fields['category'] = TreeNodeChoiceField(queryset=queryset,
                                                      empty_label='Выберите категорию',
                                                      label='Категория',
                                                      required=True)
