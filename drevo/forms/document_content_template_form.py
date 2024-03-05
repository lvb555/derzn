from django.forms import Form, CharField, IntegerField
from django.forms import TextInput
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
        label='Содержание')
    pk = IntegerField(
        widget=TextInput(attrs={'type': 'hidden'}),
        required=False)
    zn_pk = IntegerField(
        widget=TextInput(attrs={'type': 'hidden', 'id': 'document_pk'}),
        required=False)
