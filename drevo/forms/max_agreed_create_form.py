from ckeditor.widgets import CKEditorWidget
from django import forms
from django.forms import inlineformset_factory

from drevo.models import MaxAgreedQuestion
from drevo.models.utils import get_model_or_stub


class MaxAgreedQuestionCreateForm(forms.ModelForm):
    """
    Форма создания сущности MaxAgreedQuestion
    """
    max_agreed = forms.IntegerField(widget=forms.NumberInput)


    class Meta:
        model = MaxAgreedQuestion
        exclude = ('id','max_agreed','author',)
