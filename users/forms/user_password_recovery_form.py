from django import forms
from users.models import User


class UserPasswordRecoveryForm(forms.Form):
    email = forms.CharField(
        widget=forms.EmailInput(attrs={'placeholder': 'Введите адрес электронной почты'}),
        label='E-mail'
    )

    class Meta:
        model = User
        fields = ('email',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control py-2'
