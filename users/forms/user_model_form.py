from django import forms
from users.models import User


class UserModelForm(forms.ModelForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'readonly': True}),
        label='Имя пользователя',
    )
    email = forms.CharField(
        widget=forms.EmailInput(attrs={'readonly': True}),
        label='Адрес эл. почты'
    )
    first_name = forms.CharField(
        widget=forms.TextInput(),
        label='Имя',
        required=False,
    )
    last_name = forms.CharField(
        widget=forms.TextInput(),
        label='Фамилия',
        required=False,
    )
    is_public = forms.BooleanField(
        widget=forms.CheckboxInput(),
        required=False,
    )
    job = forms.CharField(
        widget=forms.TextInput(),
        label='Профессия',
        required=False,
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'is_public', 'job')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control py-2'
