from django import forms
from django.contrib.auth.forms import SetPasswordForm
from users.models import User


class UserSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Придумайте пароль'}),
        label='Пароль'
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Подтвердите пароль'}),
        label='Повторить пароль'
    )

    class Meta:
        model = User
        fields = ('new_password1', 'new_password2')

    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control py-2'
