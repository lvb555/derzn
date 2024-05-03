from django import forms
from django.contrib.auth.forms import UserCreationForm
from users.models import User

GENDER_CHOICES = (
    ('M', 'Мужской'),
    ('F', 'Женский'),
)


class UserRegistrationForm(UserCreationForm):

    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Введите имя пользователя'}),
        label='Имя пользователя'
    )
    email = forms.CharField(
        widget=forms.EmailInput(attrs={'placeholder': 'Введите адрес электронной почты'}),
        label='Адрес эл. почты'
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Придумайте пароль'}),
        label='Пароль'
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Подтвердите пароль'}),
        label='Подтверждение пароля'
    )
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Введите имя пользователя'}),
        label='Имя пользователя'
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Введите фамилию пользователя'}),
        label='Имя пользователя'
    )
    patronymic = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Введите отчество пользователя'}),
        label='Отчество',
        required=False
    )
    gender = forms.ChoiceField(
        choices=GENDER_CHOICES,
        label='Пол',
        widget=forms.RadioSelect(attrs={'class': 'custom-class'})
    )
    birthday_at = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Дата рождения'
    )
    image = forms.ImageField(
        widget=forms.FileInput(),
        label='Аватар',
        required=False
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'first_name', 'patronymic', 'last_name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name not in ('image', 'gender'):
                field.widget.attrs['class'] = 'form-control py-2 text-grey'
            elif field_name in ('image',):
                field.widget.attrs['class'] = 'form-control text-grey'
            else:
                field.widget.attrs['class'] = 'm-0 p-0 text-grey'

    def validate_avatar_size(self):
        max_file_size = 1048576
        image = self.cleaned_data.get('image')

        if not image:
            return None, None

        if image.size > max_file_size:
            return image, 'Ошибка! Максимальный размер загружаемого файла - 1 МБ.'

        return image, None
