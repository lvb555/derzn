from django.forms import Textarea, NumberInput
from django import forms
from drevo.models import Var, Znanie, Turple
from django.core.exceptions import ValidationError


class VarForm(forms.Form):
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

    available_sctructures = (('', 'Выберите структуру'), ) + Var.available_sctructures  # допустимые типы структрур объектов
    available_types_of_content = (('', 'Выберите тип данных'), ) + Var.available_types_of_content  # допустимые типы содержимого

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

        # Указана ли редактируемая переменная
        if action == 'edit' and var is None:
            raise ValidationError('Не задан редактируемый объект')

        # Проверка на то, что типы объектов и данных находятся в своих рамках
        if not (0 <= type_of < len(Var.available_types_of_content)):
            raise ValidationError(f'Нельзя привести число {type_of} к типу данных')

        # Проверка на уникальность имени
        count = Var.objects.filter(knowledge=zn, name=name).count()
        count -= int(action == 'edit' and var.name == name)
        if count > 0:
            raise ValidationError(f'Объект с именем {name} уже существует в контексте этого документа')

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
    connected_to = forms.ModelChoiceField(queryset=Var.objects.all(), label='Родитель', required=False, empty_label='Без подчинения')
    turple = forms.ModelChoiceField(queryset=Turple.objects.all(), label='Справочник', required=False, empty_label='Новый справочник')
    fill_title = forms.CharField(
        label='Заголовок для окна диалога',
        required=False,
        widget=Textarea(attrs={
            'cols': 10,
            'rows': 10,
            'class': 'form-control edit-menu__textarea',
            'id': 'fill-title'}))
    knowledge = forms.ModelChoiceField(queryset=Znanie.objects.all(), widget=NumberInput(attrs={'type': 'hidden'}))
    pk = forms.ModelChoiceField(queryset=Var.objects.all(), required=False)
    action = forms.CharField(max_length=100)
    comment = forms.CharField(max_length=255, label='Комментарий', required=False)
