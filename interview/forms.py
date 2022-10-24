from unicodedata import category

from django import forms
from django.forms.models import BaseInlineFormSet, inlineformset_factory
from drevo.models.knowledge import Znanie

from interview.models import (Interview, InterviewQuestion, Question,
                              QuestionAnswer)


class ElementInLineFormSet(BaseInlineFormSet):

    def clean(self):
        """Проверка заполнености полей и элементов интервью."""
        super(ElementInLineFormSet, self).clean()
        if any(self.errors):
            return
        if not any(cleaned_data and not cleaned_data.get('DELETE', False)
                   for cleaned_data in self.cleaned_data):
            raise forms.ValidationError(
                'Нужно добавить хоть один элемент'
            )


class ZnForm(forms.ModelForm):
    name = forms.CharField(max_length=258, label='Тема интервью')
    class Meta:
        model = Znanie
        fields = ['name', 'category', 'author']

class InterviewForm(forms.ModelForm):
    class Meta:
        model = Interview
        fields = ['date_from', 'date_to']


class QuestionForm(forms.ModelForm):
    class Meta:
        model = InterviewQuestion
        fields=['question', 'nmbr_answers']


class AnswerForm(forms.ModelForm):
    class Meta:
        model = QuestionAnswer
        fields = ['answer']


class BaseQuestionFormset(ElementInLineFormSet):
    def add_fields(self, form, index) -> None:
        super(BaseQuestionFormset, self).add_fields(form, index)

    def save(self, commit=False):
        result = super(BaseQuestionFormset, self).save(commit=commit)

        for form in self.forms:
            if hasattr(form, 'nested'):
                if not self._should_delete_form(form):
                    form.nested.save(commit=commit)
        return result


QuestionFormset = inlineformset_factory(
    Interview,
    InterviewQuestion,
    formset=BaseQuestionFormset,
    form=QuestionForm,
    extra=1)

AnswerFormset = inlineformset_factory(
    Question,
    QuestionAnswer,
    formset=BaseQuestionFormset,
    form=AnswerForm,
    extra=1
)
