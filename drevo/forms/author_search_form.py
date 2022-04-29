from django import forms
from ..models import AuthorType

from .custom_choice_field import CustomChoiceField
from .select_with_input import SelectWithInput
from ..models.utils import get_model_or_stub


class AuthorSearchForm(forms.Form):
    """
    Форма для фильтрации авторов по критериям.
    """
    author_type_choices = [(author_type, author_type)
                           for author_type in get_model_or_stub(AuthorType).objects.order_by('name').values_list('name', flat=True)]

    # Поиск по имени автора и по сведениям об авторе
    main_search = forms.CharField(label="",
                                  max_length=255,
                                  widget=forms.TextInput(
                                      attrs={'class': 'form-control',
                                             'placeholder': 'Основной поиск'}),
                                  required=False)

    # Тип автора
    author_type = CustomChoiceField(label="Тип автора",
                                    choices=author_type_choices,
                                    widget=SelectWithInput(
                                        attrs={'class': 'form-control',
                                               'placeholder': 'Выберите вид знания'}),
                                    required=False)
