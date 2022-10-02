from django import forms

from drevo.models import Relation


class RelationAdminForm(forms.ModelForm):
    """
    Форма для вывода сущнусти Связь в админке
    """

    send_flag = forms.BooleanField(required=False, label='Отправить уведомления?')

    class Meta:
        model = Relation
        fields = '__all__'
