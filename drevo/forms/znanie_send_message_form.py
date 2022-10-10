from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import validate_email


class ZnanieSendMessage(forms.Form):
    """
        Форма для составления сообщения с информацией о знании.
    """
    email_address = forms.CharField(
        label='Адрес',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Укажите адрес получателя'}),
    )
    mes_text = forms.CharField(
        label='Текст сообщения',
        widget=forms.Textarea(attrs={'class': 'form-control'}),
        required=False
    )

    def clean_email_address(self):
        email = self.cleaned_data['email_address']
        if '@' not in email:
            raise ValidationError('Адрес электронной почты должен содержать символ @. Пример: email_address@mail.ru')
        elif email.endswith('@'):
            raise ValidationError('Введите часть адреса после символа "@". Пример: email_address@mail.ru')
        elif '.' not in email.split('@')[1]:
            raise ValidationError('После символа @ необходима точка. Пример: email_address@mail.ru')
        validate_email(email)
        return email
