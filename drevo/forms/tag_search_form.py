from django import forms


class TagSearchForm(forms.Form):
    """
    Форма для фильтрации тегов.
    """

    main_search = forms.CharField(label="",
                                  max_length=255,
                                  widget=forms.TextInput(
                                      attrs={'class': 'form-control',
                                             'placeholder': 'Основной поиск'}),
                                  required=False)
