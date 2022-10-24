from django.contrib import admin

from .forms import ElementInLineFormSet
from .models import Interview, InterviewQuestion, Question, QuestionAnswer


# Вспомогательные модели
class AnswerInLine(admin.TabularInline):
    """Регистрация встроенных полей ответов"""
    model = QuestionAnswer
    formset = ElementInLineFormSet
    extra = 1


class InterviewQuestionInLine(admin.TabularInline):
    """Встроенные поля и установка кол-ва ответов"""
    model = InterviewQuestion
    formset = ElementInLineFormSet
    fields = ['c_question', 'question', 'nmbr_answers']
    extra = 1

    
# Основные модели админки
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['name', 'count_answer']
    search_fields = ['name']
    inlines = [AnswerInLine]


@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    list_display = ['name', 'author', 'date_from', 'date_to', 'is_published']
    search_fields = ['name', 'author', 'date_from', 'date_to']
    inlines = [InterviewQuestionInLine]
