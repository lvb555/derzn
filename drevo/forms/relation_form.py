from django import forms
from django.urls import reverse_lazy

from drevo.models import Relation
from drevo.models import Znanie
from drevo.models import Tr, Tz



class RelationAdminForm(forms.ModelForm):
    """
    Форма для вывода сущности Связь в админке
    """

    send_flag = forms.BooleanField(required=False, label='Отправить уведомления?')
    bz_url = forms.CharField(widget=forms.HiddenInput(attrs={"id": "test_res", "data-url": reverse_lazy("test_response")}))

    class Meta:
        model = Relation
        fields = '__all__'