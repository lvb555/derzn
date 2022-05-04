import datetime

from django import forms
from django.core.exceptions import ValidationError


class DateNewForm(forms.Form):
    """Form for handling date to search
    from
    """
    week_ago = datetime.date.today() - datetime.timedelta(days=7)

    day = forms.IntegerField(label='число', initial=week_ago.day, min_value=1,
                             max_value=31)
    month = forms.IntegerField(label='месяц', initial=week_ago.month,
                               min_value=1, max_value=12)
    year = forms.IntegerField(label='год', initial=week_ago.year, min_value=0,
                              max_value=datetime.date.today().year)
    #
    def clean(self):
        cleaned_data = super().clean()
        _today = datetime.date.today()
        today_date = _today
        day = cleaned_data.get('day', today_date.day)
        month = cleaned_data.get('month', today_date.month)
        year = cleaned_data.get('year', today_date.year)
        try:
            date_entered = datetime.date(year, month, day)
        except ValueError:
            raise ValidationError('Пожалуйста, введите существующую дату')
        if date_entered > _today:
            raise ValidationError('Следующую дату можно будет ввести позже')
