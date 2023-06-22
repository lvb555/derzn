from django.db import models
from users.models import User


class Appeal(models.Model):
    SUBJECT_CHOICES = [
        ('question', 'Задать вопрос'),
        ('proposal', 'Сделать предложение по развитию сайта'),
        ('complaint', 'Заявить претензию'),
        ('profile_deletion', 'Удалить свой профиль'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='addresser'
    )
    subject = models.CharField(
        max_length=200,
        choices=SUBJECT_CHOICES,
        verbose_name='Причина обращения'
    )
    topic = models.CharField(
        max_length=255,
        verbose_name='Тема',
        blank=True
    )
    description = models.TextField(
        max_length=1000,
        verbose_name='Текст сообщения'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата обращения'
    )
    resolved = models.BooleanField(
        default=False,
        verbose_name='Отвечено'
    )
    admin = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name='Ответивший на обращение',
        related_name='addressee',
        null=True,
        blank=True
    )
    message = models.TextField(
        max_length=1000,
        verbose_name='Ответ на обращение',
        blank=True
    )
    answered_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата ответа',
        null=True,
        blank=True
    )


    class Meta:
        verbose_name = 'Обращение в поддержку'
        verbose_name_plural = 'Обращения в поддержку'
