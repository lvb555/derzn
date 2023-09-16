from django.db import models
from users.models import User
from .knowledge import Znanie
from .questions import QuestionToKnowledge


class UserAnswerToQuestion(models.Model):
    """
    Класс для описания Ответа

    """
    title = 'Ответы'
    knowledge = models.ForeignKey(
        Znanie,
        on_delete=models.PROTECT,
        verbose_name="Знание",
        related_name="answer"
    )
    question = models.ForeignKey(
        QuestionToKnowledge,
        on_delete=models.CASCADE,
        verbose_name="Вопрос",
        related_name="answer"
    )
    answer = models.TextField(
        max_length=2048,
        blank=True,
        null=True,
        verbose_name='Ответ'
    )
    answer_file = models.FileField(
        verbose_name="Файл"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name="Пользователь",
        related_name="answer"
    )
    accepted = models.BooleanField(
        default=False,
        verbose_name="Ответ принят"
    )
    date = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата создания"
    )

    def __str__(self):
        return self.answer

    class Meta:
        verbose_name = 'Ответ на вопрос'
        verbose_name_plural = 'Ответы на вопросы пользователя'  
