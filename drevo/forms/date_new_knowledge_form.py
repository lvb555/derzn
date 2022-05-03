import datetime

from django import forms

class DateNewForm(forms.Form):
    """Form for handling date to search
    from
    """
    week_ago = datetime.date.today() - datetime.timedelta(days=7)

    day = forms.IntegerField(label='число', initial=week_ago.day)
    month = forms.IntegerField(label='месяц', initial=week_ago.month)
    year = forms.IntegerField(label='год', initial=week_ago.year)
