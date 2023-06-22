from django import forms

SUBJECT_CHOICES = [
    ('question', 'Задать вопрос'),
    ('proposal', 'Сделать предложение по развитию сайта'),
    ('complaint', 'Заявить претензию'),
    ('profile_deletion', 'Удалить свой профиль'),
]


class TicketForm(forms.Form):
    subject = forms.ChoiceField(choices=SUBJECT_CHOICES, label='Причина обращения')
    topic = forms.CharField(widget=forms.TextInput(), label='Тема', required=False)
    description = forms.CharField(widget=forms.Textarea, label='Описание (Не более 1 000 знаков)', max_length=1000)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control py-2'
