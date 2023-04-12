from django import forms


class RelationStatusesForm(forms.Form):
    """
        Форма статусов связей для этапов подготовки связей
    """
    def __init__(self, stage: str = 'create', *args, **kwargs):
        super(RelationStatusesForm, self).__init__(*args, **kwargs)
        required_statuses = {
            'create': [(None, '------')],
            'update': [
                (None, '------'),
                ('WORK_PRE', 'ПредСвязь в работе'),
                ('PRE_FIN', 'Завершенная ПредСвязь'),
                ('WORK', 'Связь в работе'),
                ('FIN', 'Завершенная Связь')
            ],
            'expertise': [
                (None, '------'),
                ('PRE_FIN', 'Завершенная ПредСвязь'),
                ('PRE_EXP', 'Экспертизв ПредСвязи'),
                ('PRE_REJ', 'Отклоненная ПредСвязь'),
                ('PRE_READY', 'Готовая ПредСвязь')
            ],
            'publication': [
                (None, '------'),
                ('PRE_FIN', 'Завершенная ПредСвязь'),
                ('PUB_PRE', 'Опубликованная ПредСвязь'),
                ('PRE_REJ', 'Отклоненная ПредСвязь'),
                ('FIN', 'Завершенная Связь'),
                ('PUB', 'Опубликованная Связь'),
                ('REJ', 'Отклоненная Связь')
            ]
        }
        self.fields['status'].widget.choices = required_statuses.get(stage)

    status = forms.CharField(
        label='Статусы связей',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
