from django import forms
from .models import (Znanie,
                     Author,
                     AuthorType,
                     Category,
                     Tz,
                     Tr)
from ckeditor.widgets import CKEditorWidget
from mptt.forms import TreeNodeChoiceField


class CategoryForm(forms.ModelForm):
    """
    Форма для вывода сущности Category.
    """
    content = forms.CharField(widget=CKEditorWidget(attrs={'cols': 40,
                                                           'rows': 10,
                                                           }
                                                    ),
                              label='Содержание',
                              required=False
                              )

    class Meta:
        model = Category
        exclude = ('visits',)


class ZnanieForm(forms.ModelForm):
    """
    Форма для вывода сущности Знания.
    """
    name = forms.CharField(widget=forms.Textarea(attrs={'cols': 40,
                                                        'rows': 3,
                                                        }
                                                 ),
                           label='Тема'
                           )
    content = forms.CharField(widget=CKEditorWidget(attrs={'cols': 40,
                                                           'rows': 10,
                                                           }
                                                    ),
                              label='Содержание',
                              required=False
                              )
    category = TreeNodeChoiceField(queryset=Category.tree_objects.all(),
                                   empty_label="(нет категории)",
                                   label='Категория',
                                   required=False)

    class Meta:
        model = Znanie
        fields = '__all__'


class AuthorForm(forms.ModelForm):
    """
    Форма для вывода сущности Author.
    """
    info = forms.CharField(widget=CKEditorWidget(attrs={'cols': 40,
                                                        'rows': 10,
                                                        }
                                                 ),
                           label='Сведения об авторе',
                           required=False
                           )

    class Meta:
        model = Author
        fields = '__all__'


class GlossaryTermForm(forms.ModelForm):
    """
    Форма для вывода терминов глоссария.
    """
    description = forms.CharField(widget=CKEditorWidget(attrs={'cols': 40,
                                                               'rows': 10,
                                                               }
                                                        ),
                                  label='Описание',
                                  required=False
                                  )

    class Meta:
        model = Znanie
        fields = '__all__'


class AuthorsFilterForm(forms.Form):
    """
    Форма для фильтрации списка авторов по типу авторов (AuthorType).

    В поле author_type добавляем атрибут oninput для поля формы Select. Это
    необходимо для вызова JS функции в шаблоне, которая при вводе данных
    в форму, т.е. по настплении события oninput, отправляет её на сервер.
    Т.о. форма не требует кнопки типа "Отправить".
    """
    author_type = forms.ModelChoiceField(queryset=AuthorType.objects.all(),
                                         empty_label='Все',
                                         widget=forms.Select(attrs={'oninput': 'doSubmit(this.form.id)'
                                                                    })
                                         )


class CustomChoiceField(forms.ChoiceField):
    def valid_value(self, value):
        """Check to see if the provided value is a valid choice."""
        text_value = str(value).lower()
        for k, v in self.choices:
            if isinstance(v, (list, tuple)):
                # This is an optgroup, so look inside the group for options
                for k2, v2 in v:
                    if value == k2 or text_value == str(k2).lower():
                        return True
            else:
                if value == k or text_value == str(k).lower():
                    return True
        return False


class SelectWithInput(forms.Select):
    template_name = 'drevo/forms/select.html'
    option_template_name = 'drevo/forms/select_option.html'


class KnowledgeSearchForm(forms.Form):
    """
    Форма для фильтрации знаний по критериям.
    """
    knowledge_type_choices = [(knowledge_type, knowledge_type)
                              for knowledge_type in Tz.objects.order_by('name').values_list('name', flat=True)]

    knowledge_category_choices = [(knowledge_category, knowledge_category)
                                  for knowledge_category in Category.objects.order_by('name').values_list('name', flat=True)]

    source_com_choices = [(source_com, source_com)
                          for source_com in Znanie.objects.order_by('source_com').values_list('source_com', flat=True)]

    edge_kind_choices = [(edge_kind, edge_kind)
                         for edge_kind in Tr.objects.order_by('name').values_list('name', flat=True)]

    author_choices = [(author, author)
                      for author in Author.objects.order_by('name').values_list('name', flat=True)]

    # Поиск по заголовку и содержанию
    main_search = forms.CharField(label="",
                                  max_length=255,
                                  widget=forms.TextInput(
                                      attrs={'class': 'form-control',
                                             'placeholder': 'Основной поиск'}),
                                  required=False)
    # Вид знания
    knowledge_type = CustomChoiceField(label="Вид знания",
                                       choices=knowledge_type_choices,
                                       widget=SelectWithInput(
                                           attrs={'class': 'form-control',
                                                  'placeholder': 'Тезис, Вопрос'}),
                                       required=False)
    # Категория знания
    knowledge_category = CustomChoiceField(label="Категория знания",
                                           choices=knowledge_category_choices,
                                           widget=SelectWithInput(
                                               attrs={'class': 'form-control',
                                                      'placeholder': 'История, Наука'}),
                                           required=False)

    # Автор
    author = CustomChoiceField(label="Автор",
                               choices=author_choices,
                               widget=SelectWithInput(
                                   attrs={'class': 'form-control',
                                          'placeholder': 'Иванов, Петров'}),
                               required=False)
    # Вид связи
    edge_kind = CustomChoiceField(label="Вид связи",
                                  choices=edge_kind_choices,
                                  widget=SelectWithInput(
                                      attrs={'class': 'form-control',
                                             'placeholder': 'Аргумента, Контраргумент...'}),
                                  required=False)
