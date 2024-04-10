from django.forms import Form, CharField, IntegerField, ModelChoiceField
from django.forms import TextInput, Select
from drevo.models import Znanie
from ckeditor.widgets import CKEditorWidget


class ContentTemplate(Form):
    """
    Форма создания/редактирования шаблона текста в документе

    content - шаблона текста
    pk - id знания, в содержимое которого следует сохранить шаблон
    zn_pk - id знания документа, к которому относится данный шаблон
    """
    content = CharField(
        max_length=2048,
        widget=CKEditorWidget(attrs={'cols': 40, 'rows': 10, 'name': 'editor1'}),
        required=False,
        label='Содержание')
    pk = ModelChoiceField(
        widget=Select(attrs={'style': 'display:none;'}),
        queryset=Znanie.objects.all())
    zn_pk = ModelChoiceField(
        widget=Select(attrs={'style': 'display:none;', 'id': 'document_pk'}),
        queryset=Znanie.objects.all())
