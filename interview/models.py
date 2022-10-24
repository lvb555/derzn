from tabnanny import verbose

from django.contrib.auth import get_user_model
from django.db import models
from drevo.models.category import Category
from drevo.models.knowledge import Znanie

User = get_user_model()


class Question(models.Model):
    """Модель вопросов к интервью"""
    name = models.ForeignKey(
        Znanie,
        on_delete=models.CASCADE,
        related_name='question',
        verbose_name='Вопрос'
    )
    answers = models.ManyToManyField(
        Znanie,
        through='QuestionAnswer',
        related_name='answers'
    )

    class Meta:
        verbose_name='Вопрос'
        verbose_name_plural='Вопросы'

    def __str__(self) -> str:
        return '{}'.format(self.name)

    def count_answer(self):
        return self.answers.all().count()


class Interview(models.Model):
    """Основная модель шаблона интервью"""
    name = models.ForeignKey(
        Znanie, on_delete=models.CASCADE, verbose_name='Тема интервью'
    )
    date_from = models.DateField('Дата с')
    date_to = models.DateField('Дата до')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='survey',
        verbose_name='Автор интервью'
    )
    is_published = models.BooleanField('Опубликовано', default=False)

    class Meta:
        verbose_name = 'Интервью'
        verbose_name_plural = 'Интервью'
        

class QuestionAnswer(models.Model):
    """Модель связи вопрос - ответы"""
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name='question'
    )
    answer = models.ForeignKey(
        Znanie, verbose_name='Ответ', on_delete=models.CASCADE, related_name='answer'
    )


class InterviewQuestion(models.Model):
    """Вспомогательная модель интервью, список вопросов"""
    interview = models.ForeignKey(
        Interview,
        on_delete=models.CASCADE,
        related_name='interview_question',
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='interview_questions',
        verbose_name='Вопрос'
    )
    nmbr_answers = models.SmallIntegerField('Макс число ответов', default=1)

    class Meta:
        verbose_name = 'Вопросы интервью'
        verbose_name_plural = 'Вопросы интервью'

    def count_answer(self):
        return self.question.answers.all().count()
    
    def answers(self):
        return self.question.answers.all()
