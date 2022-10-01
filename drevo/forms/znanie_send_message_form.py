from django import forms


class ZnanieSendMessage(forms.Form):
    """
        Форма для составления сообщения с информацией о знании.
    """
    email_address = forms.EmailField(
        label='Адрес',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Укажите адрес получателя'})
    )
    mes_text = forms.CharField(
        label='Текст сообщения',
        widget=forms.Textarea(attrs={'class': 'form-control'})
    )
