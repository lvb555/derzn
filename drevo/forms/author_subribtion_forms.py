from django import forms
from django.forms import CheckboxInput, Select, SelectMultiple


class AuthorSubscriptionForm(forms.Form):
    """Takes author's to add to subscription from
    untaken ones
    """

    subscription_choices = forms.ChoiceField(
        choices=[], widget=SelectMultiple,
        label='Возможные подписки'
    )

    def __init__(self, *args, **kwargs):
        """takes data from view"""
        subscription_choices = kwargs.pop('subscription_choices')
        super().__init__(*args, **kwargs)
        self.fields['subscription_choices'].choices = subscription_choices


class AuthorSubscriptionDeleteForm(forms.Form):
    """Takes author to delete, proposing from
    user's subscriptions"""

    unsubscribe_choices = forms.ChoiceField(
        choices=[], widget=Select, label=''
    )

    def __init__(self, *args, **kwargs):
        unsubscribe_choices = kwargs.pop('unsubscribe_choices')
        super().__init__(*args, **kwargs)
        self.fields['unsubscribe_choices'].choices = unsubscribe_choices
