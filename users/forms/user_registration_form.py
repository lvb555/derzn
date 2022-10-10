from django import forms
from django.contrib.auth.forms import UserCreationForm
from users.models import User


class UserRegistrationForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Введите имя пользователя'}),
        label='Имя пользователя'
    )
    email = forms.CharField(
        widget=forms.EmailInput(attrs={'placeholder': 'Введите адрес эл. почты'}),
        label='Адрес эл. почты'
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Введите пароль'}),
        label='Пароль'
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Подтвердите пароль'}),
        label='Подтверждение пароля'
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control py-2'
