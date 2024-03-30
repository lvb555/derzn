from django import forms
from mptt.forms import TreeNodeChoiceField
from ..models import Znanie
from ..models.site_page import StatusType, SitePage

TYPE_CHOICES = [
    ('group', 'Группа'),
    ('page', 'Страница'),
    ('type_of_complicated_knowledge', 'Вид сложного знания'),
    ('complicated_knowledge', 'Сложное знание'),
    ('label', 'Ярлык')
]


class SitePageCreateForm(forms.ModelForm):
    """
    Форма создания сущности Страницы сайта
    """
    page = forms.ModelChoiceField(queryset=Znanie.objects, label='Выберите знание')
    status = forms.ModelChoiceField(queryset=StatusType.objects, label='Статус', required=False)
    parent = TreeNodeChoiceField(queryset=SitePage.objects, label='Выберите родителя', required=False)
    type = forms.ChoiceField(choices=TYPE_CHOICES, label='Тип', widget=forms.RadioSelect())
    base_page = TreeNodeChoiceField(queryset=SitePage.objects, label='Выберите базовую страницу', required=False)
    functional = forms.BooleanField(label='Функционал', required=False)
    design_needed = forms.BooleanField(label='Необходимость макета', required=False)
    design = forms.BooleanField(label='Макет', required=False)
    layout = forms.BooleanField(label='Верстка', required=False)
    help_page = forms.BooleanField(label='Страница помощи', required=False)
    help_page_content = forms.BooleanField(label='Контент помощи', required=False)
    notification = forms.BooleanField(label='Оповещение', required=False)
    link = forms.URLField(max_length=256, label='URL-адрес', required=False)

    class Meta:
        model = SitePage
        exclude = ('id',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name in ('page', 'status', 'parent', 'link', 'base_page', 'subscribers'):
                field.widget.attrs['class'] = 'form-control py-2 text-grey'
            else:
                field.widget.attrs['class'] = 'm-0 p-0 text-grey'


class SitePageRedactForm(forms.ModelForm):
    """
    Форма редактирования сущности Страницы сайта
    """

    class Meta:
        model = SitePage
        exclude = ('id', 'page')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['disabled'] = True
            if field_name in ('status', 'parent', 'link', 'base_page', 'subscribers'):
                field.widget.attrs['class'] = 'form-control py-2 text-grey'
            else:
                field.widget.attrs['class'] = 'm-0 p-0 text-grey'
