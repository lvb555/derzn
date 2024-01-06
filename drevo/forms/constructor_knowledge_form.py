import uuid

from django import forms
from django.db.models import Q
from django.shortcuts import get_object_or_404
from mptt.forms import TreeNodeChoiceField
from ckeditor.widgets import CKEditorWidget

from drevo.models import Znanie, Category, Tz
from drevo.models.utils import get_model_or_stub

from .knowledge_create_form import ZnanieCreateForm


def add_css_class_form_control(items):
    """Добавляет к полям формы класс «form-control» и стиль рамки"""
    for field_name, field in items:
        if field_name != 'is_send' and field_name != 'show_link' and field_name != 'notification':
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['style'] = 'border: 1px solid #dee2e6;'
        else:
            field.widget.attrs['class'] = 'form-check-input'


def special_permissions_for_user(type_of_zn, user):
    """Выбор всех категорий
     в компетенции руководителя или эксперта"""
    _categories = Category.tree_objects.exclude(is_published=False)
    result_categories = []
    for category in _categories:
        if user:
            if type_of_zn == 'table':
                experts = category.get_admin_ancestors_category()
            else:
                experts = category.get_expert_ancestors_category()
            if user in experts:
                result_categories.append(category)

    queryset = get_model_or_stub(Category).objects.filter(pk__in=[category.pk for category in result_categories])

    return queryset


class MainZnInConstructorCreateEditForm(ZnanieCreateForm):
    """Форма создания и редактирования главного Знания для конструкторов сложных знаний (все конструкторы)"""
    content = forms.CharField(widget=CKEditorWidget(attrs={
                                                           'cols': 40,
                                                           'rows': 10,
                                                           }
                                                    ),
                              label='Содержание',
                              required=False
                              )

    def __init__(self, user, type_of_zn='default', *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Присваивание вида знания
        if type_of_zn == 'table':
            self.fields['tz'].initial = Tz.objects.get(name='Таблица')
        elif type_of_zn == 'test':
            self.fields['tz'].initial = Tz.objects.get(name='Тест')
        elif type_of_zn == 'algorithm':
            self.fields['tz'].initial = Tz.objects.get(name='Алгоритм')
        elif type_of_zn == 'document':
            self.fields['tz'].initial = Tz.objects.get(name='Документ')

        self.fields['tz'].widget = forms.HiddenInput()

        # Динамическое присвоение уникального ID виджету CKEditor
        self.fields['content'].widget.attrs['id'] = uuid.uuid4()

        # Выбор всех категорий в компетенции конкретного пользователя
        self.fields['category'] = TreeNodeChoiceField(queryset=special_permissions_for_user(type_of_zn, user),
                                                      empty_label='Выберите категорию',
                                                      label='Категория',
                                                      required=True)
        add_css_class_form_control(self.fields.items())

class ZnanieForCellCreateForm(forms.ModelForm):
    """
    Форма создания сущности Знание для ячейки в таблице (страница «Наполнение таблиц»)
    """
    content = forms.CharField(widget=CKEditorWidget(attrs={'cols': 40,
                                                           'rows': 10,
                                                           }
                                                    ),
                              label='Содержание',
                              required=False
                              )
    class Meta:
        model = Znanie
        fields = ('name', 'category', 'tz', 'content', 'href', 'source_com', 'order', 'author')

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Динамическое присвоение уникального ID виджету CKEditor
        self.fields['content'].widget.attrs['id'] = uuid.uuid4()

        # Выбор всех категорий в компетенции конкретного пользователя
        self.fields['category'] = TreeNodeChoiceField(queryset=special_permissions_for_user('filling_tables', user),
                                                      empty_label='Выберите категорию',
                                                      label='Категория',
                                                      required=False)

        add_css_class_form_control(self.fields.items())


class NameOfZnCreateUpdateForm(forms.ModelForm):
    """Форма создания и редактирования темы знания (конструктор таблиц)"""
    name = forms.CharField(widget=forms.Textarea(attrs={'cols': 40,
                                                        'rows': 4,
                                                        }
                                                 ),
                           label='Тема'
                           )

    class Meta:
        model = Znanie
        fields = ('name', 'tz')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tz'].initial = Tz.objects.get(name='Заголовок')
        self.fields['tz'].widget = forms.HiddenInput()
        add_css_class_form_control(self.fields.items())


class ZnanieForRowOrColumnForm(NameOfZnCreateUpdateForm):
    """Форма создания знания для строки/столбца таблицы (конструктор таблиц)"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tz'] = forms.ModelChoiceField(
            queryset=Tz.objects.filter(Q(name='Заголовок') | Q(name='Группа')).order_by('name'),
            label='Вид знания',
            required=True
        )
        add_css_class_form_control(self.fields.items())


class OrderOfRelationForm(forms.Form):
    """
    """
    order_of_relation = forms.CharField(widget=forms.TextInput(attrs={'cols': 40,
                                                                      'rows': 1,
                                                                      }
                                                               ),
                                        label='Номер связи', required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_css_class_form_control(self.fields.items())


class QuestionToQuizCreateEditForm(NameOfZnCreateUpdateForm):
    """Форма создания вопроса теста (конструктор тестов)"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tz'] = forms.ModelChoiceField(
            queryset=Tz.objects.filter(Q(name='Вопрос') | Q(name='Вопрос теста')).order_by('name'),
            label='Вид знания',
            required=True
        )
        add_css_class_form_control(self.fields.items())


class AnswerToQuizCreateEditForm(NameOfZnCreateUpdateForm):
    """Форма создания ответа теста (конструктор тестов)"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tz'].initial = Tz.objects.get(name='Ответ теста')
        self.fields['tz'].widget = forms.HiddenInput()
        add_css_class_form_control(self.fields.items())


class AnswerCorrectForm(forms.Form):
    """
    Форма с полем, которое определяет связь для ответа (Ответ верный/неверный) (конструктор тестов)
    """
    answer_correct = forms.BooleanField(label='Верный ответ', required=False,
                                        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))


class ZnForAlgorithmCreateUpdateForm(forms.ModelForm):
    """Форма для создания дочернего знания (конструктор алгоритмов)"""
    content = forms.CharField(widget=CKEditorWidget(attrs={
                                                           'cols': 40,
                                                           'rows': 10,
                                                           }
                                                    ),
                              label='Содержание',
                              required=False
                              )

    class Meta:
        model = Znanie
        fields = ('name', 'tz', 'content', 'href', 'source_com')

    def __init__(self, *args, **kwargs):
        tz_id = kwargs.pop('tz_id', None)
        super().__init__(*args, **kwargs)

        # Динамическое присвоение id CKEditor для корректного отображения нескольких виджетов
        self.fields['content'].widget.attrs['id'] = uuid.uuid4()
        
        if tz_id:
            self.fields['tz'].initial = get_object_or_404(Tz, id=tz_id)
            self.fields['tz'].widget = forms.HiddenInput()

        add_css_class_form_control(self.fields.items())
