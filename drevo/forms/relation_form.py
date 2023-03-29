from django import forms
from django.db.models import Q

from drevo.models import Relation, RelationshipTzTr, Znanie, Tr


class RelationAdminForm(forms.ModelForm):
    """
    Форма для вывода сущнусти Связь в админке
    """
    send_flag = forms.BooleanField(required=False, label='Отправить уведомления?')

    def __init__(self, *args, **kwargs):
        super(RelationAdminForm, self).__init__(*args, **kwargs)
        if not self.instance.pk and not self.data:
            self.fields['tr'].disabled = True
            self.fields['rz'].disabled = True
        elif self.instance.pk and not self.data:
            self.refresh_selects_lists()

    def refresh_selects_lists(self) -> None:
        """
            Заполнение вложенных списков на основе данных из таблицы "Взаимосвязи видов знаний и связей"
        """
        base_knowledge_tz = self.instance.bz.tz_id
        tr = self.instance.tr

        req_relationship = (
            RelationshipTzTr.objects
            .filter((Q(base_tz_id=base_knowledge_tz) | Q(base_tz=None)) & (Q(rel_type_id=tr.id) | Q(rel_type=None)))
            .values('rel_type', 'rel_tz')
            .distinct()
        )
        if not req_relationship:
            return

        rel_type_pk = [relationship.get('rel_type') for relationship in req_relationship]
        if None in rel_type_pk:
            self.fields['tr'].queryset = Tr.objects.all()
        else:
            self.fields['tr'].queryset = Tr.objects.filter(pk__in=rel_type_pk).distinct()

        rel_tz_pk = [relationship.get('rel_tz') for relationship in req_relationship]
        if None in rel_tz_pk:
            self.fields['rz'].queryset = Znanie.objects.all()
        else:
            self.fields['rz'].queryset = Znanie.objects.filter(tz_id__in=rel_tz_pk).distinct()

    class Meta:
        model = Relation
        fields = '__all__'
