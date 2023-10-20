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
    need_file = models.BooleanField(
        default=False,
        verbose_name='Файл'
    )
    publication = models.BooleanField(
        default=False,
        verbose_name="Опубликовано?"
    )

    def __str__(self):
        return self.question

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы пользователям'