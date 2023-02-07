from django import forms

from drevo.models import Relation
from drevo.models import Znanie
from drevo.models import Tr, Tz

from dal import autocomplete

class RelationAdminForm(forms.ModelForm):
    """
    Форма для вывода сущности Связь в админке


    # Используется пакет django-autocomplete-light (в импорте dal) для автообновления dropdown поля.

    # Происходит фильтрация знания по выбранному виду связи.
    # Если изначально выбирается знание, то происходит фильтрация доступных видов связи
    # На основе модели Взаимосвязи видов
    """

    # base_zn = forms.ModelChoiceField(
    #     queryset=Znanie.objects.all(),
    #     widget=autocomplete.ModelSelect2(
    #         url='knowledge_autocomplete',
    #         forward=('self.base_zn', 'bz')
    #     )
    # )
    
    # relation_type = forms.ModelChoiceField(
    #     queryset=Tr.objects.all(),
    #     widget=autocomplete.ModelSelect2(
    #         url='relation_autocomplete',
    #         forward=('self.relation_type', 'tr')
    #     )
    # )

    # related_knowledge = forms.ModelChoiceField(
    #     queryset=Znanie.objects.all(),
    #     widget=autocomplete.ModelSelect2(
    #         url='knowledge_autocomplete',
    #         forward=('self.base_zn', 'bz')
    #     )
    # )

    send_flag = forms.BooleanField(required=False, label='Отправить уведомления?')

    class Meta:
        model = Relation
        fields = '__all__'
        # widgets = {
        #     'Базовое знание': autocomplete.ModelSelect2(url='knowledge_autocomplete', forward=('base_zn', 'bz')),
        #     'Вид связи':  autocomplete.ModelSelect2(url='relation_autocomplete',forward=('base_zn', 'bz')),
        #     'Связанное знание': autocomplete.ModelSelect2(url='knowledge_autocomplete', forward=('base_zn', 'bz')),            
        # }
