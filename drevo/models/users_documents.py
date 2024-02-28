from django.db import models

from users.models import User
from .knowledge import Znanie


class UsersDocuments(models.Model):
    """
    Класс для пользовательских документов"
    """
    
    title = 'Документ пользователя'
    root_document = models.ForeignKey(
        Znanie,
        on_delete=models.CASCADE,
        verbose_name='Родительский документ'
    )    
    name = models.CharField(
        max_length=255,
        verbose_name='Название пользовательского документа',
    )
    content = models.TextField(
        verbose_name='Содержание',
        default="",
        blank=True,
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    is_complete = models.BooleanField(
        default=False,
        verbose_name='Завершено'
    )
    changed_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Последнее изменение'
    )
    pdf = models.FileField(
        upload_to='pdf/',
        null=True,
        blank=True,
        verbose_name='PDF'
    )
    word = models.FileField(
        upload_to='word/',
        null=True,
        blank=True,
        verbose_name='WORD'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Документ пользователя'
        verbose_name_plural = 'Документы пользователей'
