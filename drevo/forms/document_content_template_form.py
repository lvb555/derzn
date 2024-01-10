from django.forms import Form, CharField, IntegerField
from django.forms import TextInput, Textarea


class ContentTemplate(Form):
    content = CharField(
        max_length=2048,
        widget=Textarea(attrs={
            'cols': 20, 
            'rows': 20, 
            'class': 'form-control', 
            'placeholder':'Шаблон текста'}),
        label='Содержание')
    pk = IntegerField(
        widget=TextInput(attrs={'type': 'hidden'}),
        required=False)
    zn_pk = IntegerField(
        widget=TextInput(attrs={'type': 'hidden', 'id': 'document_pk'}),
        required=False)
