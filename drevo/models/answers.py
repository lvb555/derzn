from django.db import models
from users.models import User
from .knowledge import Znanie
from .questions import QuestionToKnowledge
from .refuse_reason import RefuseReason
from ..common.file_storage import ASCIIFileSystemStorage


class UserAnswerToQuestion(models.Model):
    """
    Класс для описания Ответа

    """
    title = 'Ответы'
    knowledge = models.ForeignKey(
        Znanie,
        on_delete=models.CASCADE,
        verbose_name="Знание"
    )
    question = models.ForeignKey(
        QuestionToKnowledge,
        on_delete=models.CASCADE,
        verbose_name="Вопрос"
    )
    answer = models.TextField(
        max_length=2048,
        blank=True,
        null=True,
        verbose_name='Ответ'
    )
    answer_file = models.FileField(
        max_length=255,
        upload_to="proof/",
        verbose_name="Файл",
        null=True,
        blank=True,
        storage=ASCIIFileSystemStorage()
    )
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name="Пользователь"
    )
    accepted = models.BooleanField(
        default=False,
        verbose_name="Ответ принят"
    )
    inspector = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        default=None,
        null=True,
        blank=True,
        verbose_name="Проверил эксперт",
        related_name="inspector"
    )
    refuse_reason = models.ForeignKey(
        RefuseReason,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Причина отказа"
    )
    date = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата создания"
    )

    def __str__(self):
        return self.answer

    class Meta:
        verbose_name = 'Ответ на вопрос'
        verbose_name_plural = 'Ответы на вопросы'  
