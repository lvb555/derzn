from django import forms
from users.models import User, Profile

GENDER_CHOICES = (
    ('M', 'Мужской'),
    ('F', 'Женский'),
)


class ProfileModelForm(forms.ModelForm):

    gender = forms.ChoiceField(
        choices=GENDER_CHOICES,
        label='Пол',
        widget=forms.RadioSelect()
    )
    birthday_at = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'placeholder': 'Введите дату рождения'}),
        label='Дата рождения'
    )
    image = forms.ImageField(
        widget=forms.FileInput(),
        label='Аватар',
        required=False,
    )

    class Meta:
        model = User
        fields = ('gender', 'birthday_at', 'image')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name not in ('image', 'gender'):
                field.widget.attrs['class'] = 'form-control py-2 text-grey h-auto'
            elif field_name in ('image',):
                field.widget.attrs['class'] = 'form-control text-grey h-auto'
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
