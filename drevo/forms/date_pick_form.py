import datetime

from django import forms
from django.core.exceptions import ValidationError


class DatePickNewForm(forms.Form):
    """Форма поиска знаний по дате публикации"""
    week_ago = datetime.date.today() - datetime.timedelta(days=7)

    date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'datepicker',
            'value': week_ago.strftime('%Y-%m-%d'),
        },
        ),
        label='Показать знания, начиная с:',
    )

    def clean(self):
        """Форма обрабатывает только прошедшее время"""
        _today = datetime.date.today()
        date_picked = self.cleaned_data.get('date')
        if date_picked and date_picked > _today:
            raise ValidationError('Дату можно изменить.')