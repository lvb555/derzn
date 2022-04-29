from .select_with_input import SelectWithInput
from django import forms
from ..models import AuthorType

from ckeditor.widgets import CKEditorWidget
from mptt.forms import TreeNodeChoiceField
from ..models.utils import get_model_or_stub


class AuthorsFilterForm(forms.Form):
    """
    Форма для фильтрации списка авторов по типу авторов (AuthorType).

    В поле author_type добавляем атрибут oninput для поля формы Select. Это
    необходимо для вызова JS функции в шаблоне, которая при вводе данных
    в форму, т.е. по наступлении события oninput, отправляет её на сервер.
    Т.о. форма не требует кнопки типа "Отправить".
    """
    author_type = forms.ModelChoiceField(
        queryset=get_model_or_stub(AuthorType).objects.order_by(
            'name').values_list('name', flat=True),
        empty_label='Все',
        widget=SelectWithInput(attrs={'class': 'form-control',
                                      'oninput': 'doSubmit(this.form.id)'})
    )
