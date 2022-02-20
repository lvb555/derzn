from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.forms import SetPasswordForm, PasswordChangeForm
from django.core.exceptions import ValidationError

from users.models import User, Profile


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Введите имя пользователя',
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Введите пароль',
    }))

    class Meta:
        model = User
        fields = ('username', 'password')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control py-2'


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

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control py-2'


class ProfileModelForm(forms.ModelForm):
    patronymic = forms.CharField(
        widget=forms.TextInput(),
        label='Отчество',
        required=False,
    )
    gender = forms.ChoiceField(
        choices=Profile.GENDERS,
        widget=forms.Select(),
        label='Пол',
    )
    birthday_at = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Дата рождения',
        required=False,
    )
    image = forms.ImageField(
        widget=forms.FileInput(),
        label='Аватар',
        required=False,
    )

    class Meta:
        model = User
        fields = ('patronymic', 'gender', 'birthday_at', 'image')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name not in ('image',):
                field.widget.attrs['class'] = 'form-control py-2'
            else:
                field.widget.attrs['class'] = 'form-control'

    def validate_avatar_size(self):
        max_file_size = 1048576
        image = self.cleaned_data.get('image')

        if not image:
            return None, None

        if image.size > max_file_size:
            return image, 'Ошибка! Максимальный размер загружаемого файла - 1 МБ.'

        return image, None


class UserPasswordRecoveryForm(forms.Form):
    email = forms.CharField(
        widget=forms.EmailInput(),
        label='Адрес эл. почты'
    )

    class Meta:
        model = User
        fields = ('email',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control py-2'


class UserSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Введите новый пароль'}),
        label='Новый пароль'
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Подтвердите пароль'}),
        label='Подтверждение пароля'
    )

    class Meta:
        model = User
        fields = ('new_password1', 'new_password2')

    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control py-2'
