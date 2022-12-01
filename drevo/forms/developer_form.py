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
                            required=False,
                            label='Комментарий'
                           )
    admin = forms.CharField(widget=forms.Textarea(attrs={'cols': 60,
                                                        'rows': 3,
                                                        }
                                                 ),
                            required=False,
                            label='Админ'
                           )
    contribution = forms.IntegerField(initial=0,)
    

    class Meta:
        model = Developer
        fields = '__all__'