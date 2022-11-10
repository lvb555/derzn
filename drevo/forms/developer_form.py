from django import forms
from drevo.models.developer import Developer

class DeveloperForm(forms.ModelForm):
    """
    Форма для вывода сущности Знания.
    """
    comment = forms.CharField(widget=forms.Textarea(attrs={'cols': 60,
                                                        'rows': 3,
                                                        }
                                                 ),
                           label='Комментарий'
                           )

    class Meta:
        model = Developer
        fields = '__all__'