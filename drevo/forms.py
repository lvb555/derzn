from django import forms
from .models import Znanie

class ZnanieForm(forms.ModelForm):
    """
    Форма для вывода сущности Знания.
    """
    photo = forms.ImageField(required=False,
                             help_text='Выберите изображения для загрузки (jpg, png)',
                             allow_empty_file=True,
                             widget=forms.ClearableFileInput(attrs={'multiple': True})
                             )
    name = forms.CharField(widget=forms.Textarea(attrs={'cols': 40,
                                                        'rows': 3,
                                                        }
                                                 )
                           )
    content = forms.CharField(widget=forms.Textarea(attrs={'cols': 40,
                                                        'rows': 10,
                                                        }
                                                    )
                              )
    class Meta:
        model = Znanie
        fields = '__all__'
