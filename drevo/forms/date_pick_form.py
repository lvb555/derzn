import datetime

from django import forms
from django.core.exceptions import ValidationError


class DatePickNewForm(forms.Form):
    week_ago = datetime.date.today() - datetime.timedelta(days=7)

    date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            # 'class': 'datepicker',
            'value': week_ago.strftime('%d-%m-%Y')},
        ),
        label='Показать знания, начиная с:',
    )

    def clean(self):
        cleaned_data = super().clean()
        _today = datetime.date.today()
        date_picked = cleaned_data.get('date')
        if date_picked > _today:
            raise ValidationError('Дату можно изменить.')