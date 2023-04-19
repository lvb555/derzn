from django import forms


class RelationStatusesForm(forms.Form):
    """
        Форма статусов связей для этапов подготовки связей
    """
    def __init__(self, statuses: list, *args, **kwargs):
        super(RelationStatusesForm, self).__init__(*args, **kwargs)
        self.fields['status'].widget.choices = statuses

    status = forms.CharField(
        label='Статусы связей',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
