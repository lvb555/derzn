from django import forms
from drevo.models import RelationStatuses


class RelationStatusesForm(forms.Form):
    """
        Форма статусов связей для этапов подготовки связей
    """
    status = forms.CharField(
        label='Статусы связей',
        widget=forms.Select(choices=RelationStatuses.Status.choices, attrs={'class': 'form-control'})
    )
