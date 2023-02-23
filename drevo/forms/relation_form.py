from django import forms
from django.urls import reverse_lazy

from drevo.models import Relation
from drevo.models import Znanie
from drevo.models import Tr, Tz
from drevo.models.interconnections_of_relations import AllowedRelationCombinations



class RelationAdminForm(forms.ModelForm):
    """
    Форма для вывода сущности Связь в админке
    """

    send_flag = forms.BooleanField(required=False, label='Отправить уведомления?')
    bz_url = forms.CharField(required=False, widget=forms.HiddenInput(attrs={"id": "load_tr", "data-url": reverse_lazy("load_tr")}))
    tr_url = forms.CharField(required=False, widget=forms.HiddenInput(attrs={"id": "load_bz", "data-url": reverse_lazy("load_bz")}))

    class Meta:
        model = Relation
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        print(self.data)

        # if 'bz' in self.data:
        #     try:
        #         bz_id = int(self.data.get('bz'))
        #         allowed_tr = InteractionsOfRelations.objects.filter(base_knowledge_type=Znanie.objects.filter(id=bz_id).get().tz)
        #         allowed_list = []
        #         for elem in allowed_tr:
        #             tr = Tr.objects.filter(id=elem['relation_type_id'])
        #             allowed_list.append(tr)
        #         self.fields['tr'].queryset = allowed_list
        #     except (ValueError, TypeError):
        #         pass
        # elif self.instance.pk:
        #     allowed_tr = InteractionsOfRelations.objects.filter(base_knowledge_type=Znanie.objects.filter(id=self.instance.bz).get().tz)
        #     allowed_list = []
        #     for elem in allowed_tr:
        #         tr = Tr.objects.filter(id=elem['relation_type_id'])
        #         allowed_list.append(tr)
        #     self.fields['tr'].queryset = allowed_list