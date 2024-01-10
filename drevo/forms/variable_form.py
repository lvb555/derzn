from django.forms import ModelForm, RadioSelect, Textarea, TextInput, CheckboxInput, ModelChoiceField, NumberInput
from django import forms
from drevo.models import Var, Znanie, Turple
from django.core.exceptions import ValidationError



class VarForm(forms.Form):

    available_sctructures = (('', 'Выберите структуру'), ) + Var.available_sctructures
    available_types_of_content = (('', 'Выберите тип данных'), ) + Var.available_types_of_content

    def clean(self):

        structure_list = ['Массив', 'Переменная', 'Справочник', 'Итератор']

        cleaned_data = super().clean()

        name = cleaned_data.get('name')
        try:
            structure = int(cleaned_data.get('structure'))
        except:
            structure = None
        is_main = cleaned_data.get('is_main')
        is_global = cleaned_data.get('is_global')
        try:
            type_of = int(cleaned_data.get('type_of'))
        except:
            type_of = None
        weight = cleaned_data.get('weight')
        connected_to = cleaned_data.get('connected_to')
        turple = cleaned_data.get('turple')
        fill_title = cleaned_data.get('fill_title')
        optional = cleaned_data.get('optional')
        subscription = cleaned_data.get('subscription')
        zn = cleaned_data.get('knowledge')
        var = cleaned_data.get('pk')
        action = cleaned_data.get('action')
        comment = cleaned_data.get('comment')

        # Проверка обязательных полей поля
        l = [
        (name, 'name'), 
        (zn, 'knowledge'),
        (is_main, 'is_main'), 
        (optional, 'optional'),
        (structure, 'structure'), 
        (is_global, 'is_global'),
        (subscription, 'subscription')]

        if action not in ['edit', 'create']:
            raise ValidationError(f'Неопозднанный тип действия {action}')

        """
        Проверка на валидность введенных данных
        """
        
        for v, n in l:
            if v is None:
                raise ValidationError(f'Поле {n} должно быть заполнено')

        if action == 'edit' and var is None:
            raise ValidationError(f'Не задан редактируемый объект')

        # проверка на то, что у структур Переменная, Массив указан тип содержимого
        if structure <= 1 and type_of is None:
            a = ['Переменная', 'Массив'][structure]
            raise ValidationError(f'Поле type_of должно быть заполнено для объекта {a}')

        # Проверка на то, что типы объектов и данных находятся в своих рамках
        if type_of is not None and not (0 <= type_of < len(Var.available_types_of_content)):
            raise ValidationError(f'Нельзя привести число {type_of} к типу данных')

        if not (0 <= structure < len(Var.available_sctructures)):
            raise ValidationError(f'Нельзя привести число {structure} к типу объекта')

        # Проверка на уникальность имени
        count = Var.objects.filter(knowledge=zn, name=name).count()
        count -= int(action == 'edit' and var.name == name)
        if count > 0:
            raise ValidationError(f'Объект с именем {name} уже существует в контексте этого документа')

        # Проверка на совпадение типов структур главной и подчиняемой переменной
        if (not is_main) and (connected_to is not None) and (structure != connected_to.structure):
            raise ValidationError(f'Объект типа {Var.available_sctructures[structure][1]} не может быть подчинен объекту типа {Var.available_sctructures[connected_to.structure][1]}')


    name = forms.CharField(max_length=255, label='Имя объекта')
    structure = forms.ChoiceField(
        label='Структура',
        choices=available_sctructures
    )
    is_main = forms.BooleanField(label='Главный', required=False)
    is_global = forms.BooleanField(label='Глобальный', required=False)
    subscription = forms.BooleanField(label='Прописью', required=False)
    optional = forms.BooleanField(label='Необязательность', required=False)
    type_of = forms.ChoiceField(
        label='Тип',
        choices=available_types_of_content,
        required=False)
    weight = forms.IntegerField(required=False, label='Порядок')
    connected_to = forms.ModelChoiceField(queryset=Var.objects.all(), label='Подчинение', required=False, empty_label='Без подчинения')
    turple = forms.ModelChoiceField(queryset=Turple.objects.all(), label='Справочник', required=False, empty_label='Новый справочник')
    fill_title = forms.CharField(
        label='Текст при инициализации',
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
