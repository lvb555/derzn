from django import forms
from ..models import (Znanie,
                      Author,
                      Category,
                      Tz,
                      Tr,
                      Label)

from .custom_choice_field import CustomChoiceField
from .select_with_input import SelectWithInput
from .select_with_input_multi import SelectWithInputMulti
from ..models.utils import get_model_or_stub


class KnowledgeSearchForm(forms.Form):
    """
    Форма для фильтрации знаний по критериям.
    """
    knowledge_type_choices = [(knowledge_type, knowledge_type)
                              for knowledge_type in get_model_or_stub(Tz).objects.order_by('name').values_list('name', flat=True)]

    knowledge_category_choices = [(knowledge_category, knowledge_category)
                                  for knowledge_category in get_model_or_stub(Category).objects.order_by('name').values_list('name', flat=True)]

    source_com_choices = [(source_com, source_com)
                          for source_com in get_model_or_stub(Znanie).objects.order_by('source_com').values_list('source_com', flat=True)]

    edge_kind_choices = [(edge_kind, edge_kind)
                         for edge_kind in get_model_or_stub(Tr).objects.order_by('name').values_list('name', flat=True)]

    author_choices = [(author, author)
                      for author in get_model_or_stub(Author).objects.order_by('name').values_list('name', flat=True)]

    # Поиск по заголовку и содержанию
    main_search = forms.CharField(label="",
                                  max_length=255,
                                  help_text='Название/Содержимое знания/Комментарии к источнику',
                                  widget=forms.TextInput(
                                      attrs={'class': 'form-control',
                                             'placeholder': 'Основной поиск'}),
                                  required=False)
    main_search__name = forms.BooleanField(label="Название",
                                           initial=True,
                                           widget=forms.CheckboxInput(
                                               attrs={'class': 'form-check-input'}),
                                           required=False)

    main_search__content = forms.BooleanField(label="Содержимое знания",
                                              initial=True,
                                              widget=forms.CheckboxInput(
                                                  attrs={'class': 'form-check-input'}),
                                              required=False)

    main_search__source_com = forms.BooleanField(label="Комментирии к источнику",
                                                 initial=True,
                                                 widget=forms.CheckboxInput(
                                                     attrs={'class': 'form-check-input'}),
                                                 required=False)                        
    # Вид знания
    knowledge_type = CustomChoiceField(label="Вид знания",
                                       choices=knowledge_type_choices,
                                       widget=SelectWithInput(
                                           attrs={'class': 'form-control',
                                                  'placeholder': 'Выберите вид знания'}),
                                       required=False)
    # Категория знания
    knowledge_category = CustomChoiceField(label="Категория",
                                           choices=knowledge_category_choices,
                                           widget=SelectWithInput(
                                               attrs={'class': 'form-control',
                                                      'placeholder': 'Выберите категорию'}),
                                           required=False)

    # Автор
    author = CustomChoiceField(label="Автор",
                               choices=author_choices,
                               widget=SelectWithInput(
                                   attrs={'class': 'form-control',
                                          'placeholder': 'Выберите автора'}),
                               required=False)
    # Вид связи
    edge_kind = CustomChoiceField(label="Вид связи",
                                  choices=edge_kind_choices,
                                  widget=SelectWithInput(
                                      attrs={'class': 'form-control',
                                             'placeholder': 'Выберите вид связи'}),
                                  required=False)

    class Tag(forms.Form):
        tag_choices = [(tag_name, tag_name)
                       for tag_name in get_model_or_stub(Label).objects.order_by('name').values_list('name', flat=True)]
        # Теги
        tag = CustomChoiceField(label="Тег",
                                choices=tag_choices,
                                widget=SelectWithInputMulti(
                                    attrs={'class': 'form-control multi',
                                           'placeholder': 'Выберите Тег'}),
                                required=False)
