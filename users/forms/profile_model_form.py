from django import forms
from users.models import User, Profile


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
