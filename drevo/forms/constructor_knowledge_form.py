from django import forms
from django.db.models import Q
from mptt.forms import TreeNodeChoiceField

from drevo.models import Znanie, Category, Tz, Tr, RelationshipTzTr
from drevo.models.utils import get_model_or_stub

from .knowledge_create_form import ZnanieCreateForm
from .knowledge_form import ZnanieValidators


def add_css_class_form_control(items):
    """Добавляет к полям формы класс «form-control»"""
    for field_name, field in items:
        if field_name != 'is_send':
            field.widget.attrs['class'] = 'form-control'


def special_permissions_for_user(type_of_zn, user=None):
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
        else:
            result_categories.append(category)

    queryset = get_model_or_stub(Category).objects.filter(pk__in=[category.pk for category in result_categories])

    return queryset


class MainZnInConstructorCreateEditForm(ZnanieCreateForm):
    """Форма создания и редактирования главного Знания для конструкторов (вид «Таблица», «Тест», «Алгоритм») и всех
    знаний конструктора алгоритмов"""

    def __init__(self, user, type_of_zn='default', *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Присвоение виду знания значения в зависимости от вида конструктора
        if type_of_zn == 'table':
            self.fields['tz'].initial = Tz.objects.get(name='Таблица')
        elif type_of_zn == 'test':
            self.fields['tz'].initial = Tz.objects.get(name='Тест')
        else:
            self.fields['tz'].initial = Tz.objects.get(name='Алгоритм')

        print(self.fields['tz'].initial)

        self.fields['tz'].widget = forms.HiddenInput()

        # Выбор всех категорий в компетенции конкретного пользователя
        self.fields['category'] = TreeNodeChoiceField(queryset=special_permissions_for_user(type_of_zn, user),
                                                      empty_label='Выберите категорию',
                                                      label='Категория',
                                                      required=True)


class NameOfZnCreateUpdateForm(forms.ModelForm, ZnanieValidators):
    """Форма создания и редактирования знания с темой"""
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
                   'notification')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tz'].initial = Tz.objects.get(name='Заголовок')
        self.fields['tz'].widget = forms.HiddenInput()
        add_css_class_form_control(self.fields.items())


class ZnForAlgorithmCreateUpdateForm(ZnanieCreateForm):
    """Форма для создания дочернего знания на странице «Конструктор алгоритмов»"""

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['tz'].widget.attrs.update({'disabled': 'disabled'})

        # Выбор всех категорий в компетенции конкретного пользователя
        self.fields['category'] = TreeNodeChoiceField(queryset=special_permissions_for_user('algorithm', user),
                                                      empty_label='Выберите категорию',
                                                      label='Категория',
                                                      required=False)
        add_css_class_form_control(self.fields.items())


class RelationForZnInAlgorithm(forms.Form):
    """Форма для выбора вида связи на странице «Конструктор алгоритмов»"""
    def __init__(self, parent_zn_tz='default', *args, **kwargs):
        super(RelationForZnInAlgorithm, self).__init__(*args, **kwargs)
        # parent_zn_tz = kwargs.get('type_oz_zn')
        print(parent_zn_tz)
        relationships_with_parent_zn = RelationshipTzTr.objects.filter(base_tz=parent_zn_tz)
        rel_type_with_parent_zn = Tr.objects.filter(pk__in=[rel.rel_type_id for rel in relationships_with_parent_zn])
        self.fields['tr'] = forms.ModelChoiceField(queryset=rel_type_with_parent_zn,
                                                   empty_label='Выберите вид связи',
                                                   label='Вид связи',
                                                   required=True)
        add_css_class_form_control(self.fields.items())


class ZnanieForCellCreateForm(ZnanieCreateForm):
    """
    Форма создания сущности Знание для ячейки в таблице (для страницы «Наполнение таблиц»)
    """

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tz'].initial = Tz.objects.get(name='Заголовок')
        self.fields['tz'].widget = forms.HiddenInput()
        # Выбор всех категорий в компетенции конкретного пользователя
        self.fields['category'] = TreeNodeChoiceField(queryset=special_permissions_for_user('filling_tables', user),
                                                      empty_label='Выберите категорию',
                                                      label='Категория',
                                                      required=False)


class AttributesOfZnForm(forms.Form):
    order_of_relation = forms.CharField(widget=forms.TextInput(attrs={'cols': 40,
                                                                      'rows': 1,
                                                                      }
                                                               ),
                                        label='Номер связи', required=False)

    def __init__(self, *args, **kwargs):
        super(AttributesOfZnForm, self).__init__(*args, **kwargs)
        add_css_class_form_control(self.fields.items())


class AttributesOfAnswerForm(AttributesOfZnForm):
    is_correct = forms.BooleanField(label='Верно', required=False)

    def __init__(self, *args, **kwargs):
        super(AttributesOfZnForm, self).__init__(*args, **kwargs)
        add_css_class_form_control(self.fields.items())


class RelationCreateEditForm(NameOfZnCreateUpdateForm):
    """Форма создания Знания вида Строка или Столбец для конструктора таблиц"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tz'] = forms.ModelChoiceField(
            queryset=Tz.objects.filter(Q(name='Заголовок') | Q(name='Группа')).order_by('name'),
            label='Вид знания',
            required=True
        )
        add_css_class_form_control(self.fields.items())


class QuestionToQuizCreateForm(NameOfZnCreateUpdateForm):
    """Форма создания вопроса теста для конструктора тестов"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tz'] = forms.ModelChoiceField(
            queryset=Tz.objects.filter(Q(name='Вопрос') | Q(name='Вопрос теста')).order_by('name'),
            label='Вид знания',
            required=True
        )
        add_css_class_form_control(self.fields.items())


class AnswerToQuizCreateForm(NameOfZnCreateUpdateForm):
    """Форма создания ответа теста для конструктора тестов"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tz'].initial = Tz.objects.get(name='Ответ теста')
        self.fields['tz'].widget = forms.HiddenInput()
        add_css_class_form_control(self.fields.items())
