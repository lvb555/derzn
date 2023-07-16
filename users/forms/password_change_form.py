from django.contrib.auth.forms import PasswordChangeForm
from django import forms

class MyPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Старый пароль'}))
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Новый пароль'}))
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Подтверждение нового пароля'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control py-2 text-grey'
