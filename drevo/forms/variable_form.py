from django.forms import Textarea, NumberInput
from django import forms
from django.db.models import Q
from mptt.forms import TreeNodeChoiceField
from drevo.models import TemplateObject, Znanie, Turple
from users.models import User
from django.core.exceptions import ValidationError


class TemplateObjectAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['connected_to'] = TreeNodeChoiceField(
            queryset=TemplateObject.objects.filter(Q(knowledge=self.instance.knowledge, availability=0) |  Q(user=self.instance.user, availability=1) | Q(availability=2)),
            label='Родитель',
            required=False)
        
        self.fields['user'] = forms.ModelChoiceField(queryset=User.objects.all(), required=False)

    def clean(self):
        user = self.cleaned_data.get('user')
        availability = self.cleaned_data.get('availability')

        if availability == 1 and not user:
            raise ValidationError('У глобального объекта должен быть указан пользователь')

    class Meta:
        model = TemplateObject
        fields = '__all__'
        exclude = ['templates_that_use']


class TemplateObjectForm(forms.Form):
    """
        Форма создания/редактирования объектов шаблона документа

        name - имя объекта
        structure - структура объекта(для данной формы Переменная или Массив)
        is_main - является ли объект главным в группе
        availability - класс объекта(для данной формы Глобальный или Локальный)
        subscription - нужна ли пропись
        optional - является ли объект обязательным к заполнению
        type_of - типы данных объекта
        weight - вес, для сортировки
        connected_to - родитель объекта
        tuple - справочник всех допустимых значений, нужен, если тип данных Справочник
        fill_title - тект, показываемый пользователю при инициализации объекта
        knowledge - знание документа
        action - вид действия(создание/изменение)
        pk - редактирумей объект(нужен, если выбрано изменение)
        comment - комментарий к объекту
    """

    available_sctructures = (('', 'Выберите структуру'), ) + TemplateObject.available_sctructures  # допустимые типы структрур объектов
    available_types_of_content = (('', 'Выберите тип данных'), ) + TemplateObject.available_types_of_content  # допустимые типы содержимого

    def clean(self):
        cleaned_data = super().clean()

        name = cleaned_data.get('name')
        structure = cleaned_data.get('structure', False)
        is_main = cleaned_data.get('is_main')
        availability = cleaned_data.get('availability')
        try:
            type_of = int(cleaned_data.get('type_of'))
        except:
            type_of = None
        connected_to = cleaned_data.get('connected_to')
        optional = cleaned_data.get('optional')
        subscription = cleaned_data.get('subscription')
        zn = cleaned_data.get('knowledge')
        var = cleaned_data.get('pk')
        action = cleaned_data.get('action')
        tuple_ = cleaned_data.get('turple')

        # обязательные полей
        required_fields = [
            (name, 'name'),
            (type_of, 'type'),
            (zn, 'knowledge'),
            (is_main, 'is_main'),
            (optional, 'optional'),
            (structure, 'structure'),
            (availability, 'availability'),
            (subscription, 'subscription')
        ]

        # Ясность действия
        if action not in ['edit', 'create']:
            raise ValidationError(f'Неопозднанный тип действия {action}')

        # Проверка на то, что все обязательные поля заполнены
        for v, n in required_fields:
            if v is None:
                raise ValidationError(f'Поле {n} должно быть заполнено')

        # Проверка на то, что уровень доступа родителя и ребенка совпадают
        if connected_to and connected_to.availability < availability:
            l = [
                ('Локального', 'Локальный'),
                ('Глобального', 'Глобальный'),
                ('Общего', 'Общий')
            ]
            raise ValidationError(f'Родителем {l[availability][0]} объекта не может быть {l[connected_to.availability][1]} объект')

        # Указана ли редактируемая переменная
        if action == 'edit' and var is None:
            raise ValidationError('Не задан редактируемый объект')

        if type_of == 3 and tuple_ is None:
            raise ValidationError('Не выбран справочник')

        # Проверка на то, что типы объектов и данных находятся в своих рамках
        if not (0 <= type_of < len(TemplateObject.available_types_of_content)):
            raise ValidationError(f'Нельзя привести число {type_of} к типу данных')

        # Проверка на уникальность имени
        count = TemplateObject.objects.filter(knowledge=zn, name=name).count()
        count -= int(action == 'edit' and var.name == name)
        if count > 0:
            raise ValidationError(f'Объект с именем {name} существует уже в контексте этого документа')

    name = forms.CharField(max_length=255, label='Имя объекта')
    structure = forms.BooleanField(label='Массив', required=False)
    is_main = forms.BooleanField(label='Это группа', required=False)
    availability = forms.BooleanField(label='Глобальный объект', required=False)
    subscription = forms.BooleanField(label='Прописью', required=False)
    optional = forms.BooleanField(label='Необязательность', required=False)
    type_of = forms.ChoiceField(
        label='Вид значения',
        choices=available_types_of_content,
        required=False)
    weight = forms.IntegerField(required=False, label='Порядок')
    connected_to = TreeNodeChoiceField(queryset=TemplateObject.objects.all(), label='Родитель', required=False, empty_label='Без подчинения')
    turple = forms.ModelChoiceField(queryset=Turple.objects.all(), label='Справочник', required=False, empty_label='Новый справочник')
    fill_title = forms.CharField(
        label='Заголовок',
        required=False,
        widget=Textarea(attrs={
            'cols': 10,
            'rows': 10,
            'class': 'form-control edit-menu__textarea',
            'id': 'fill-title'}))
    knowledge = forms.ModelChoiceField(queryset=Znanie.objects.all(), widget=NumberInput(attrs={'type': 'hidden'}))
    pk = forms.ModelChoiceField(queryset=TemplateObject.objects.all(), required=False)
    action = forms.CharField(max_length=100)
    comment = forms.CharField(max_length=255, label='Комментарий', required=False)
