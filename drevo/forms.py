from django import forms
from .models import Znanie, Label
from django.db.models.functions import Lower

class ZnanieForm(forms.ModelForm):
    photo = forms.ImageField(required=False,
                             help_text='Выберите изображения для загрузки (jpg, png)',
                             allow_empty_file=True,
                             widget=forms.ClearableFileInput(attrs={'multiple': True})
                             )
    labels = forms.ModelMultipleChoiceField(queryset=Label.objects.all().order_by(Lower('name')))
    class Meta:
        model = Znanie
        fields = '__all__'
