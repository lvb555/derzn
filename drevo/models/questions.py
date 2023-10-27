from django.db import models
from users.models import User
from .knowledge import Znanie


class QuestionToKnowledge(models.Model):
    """
    Класс для описания Вопросов
    
    """
    title = 'Вопросы'
    knowledge = models.ForeignKey(
        Znanie,
        on_delete=models.CASCADE,
        verbose_name="Знание"
        )
    question = models.CharField(
        max_length=255,
        blank=False,
        verbose_name="Вопрос"
    )
    publication = models.BooleanField(
        default=False,
        verbose_name="Опубликовано?"
    )
    order = models.IntegerField(
        verbose_name='Порядок',
        blank=True,
        default=10
    )

    def __str__(self):
        return self.question

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы пользователям'