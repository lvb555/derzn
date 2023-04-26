from django.db import models
from .relation import Relation
from users.models import User


class RelationStatuses(models.Model):
    """
        Статусы связи
    """
    class Status(models.TextChoices):
        WORK_PRE = 'WORK_PRE', 'ПредСвязь в работе'
        WORK = 'WORK', 'Связь в работе'
        PRE_READY = 'PRE_READY', 'Готовая ПредСвязь'
        PRE_FINISH = 'PRE_FIN', 'Завершенная ПредСвязь'
        FINISH = 'FIN', 'Завершенная Связь'
        PRE_EXPERTISE = 'PRE_EXP', 'Экспертизв ПредСвязи'
        REJECT = 'REJ', 'Отклоненная Связь'
        PRE_REJECT = 'PRE_REJ', 'Отклоненная ПредСвязь'
        PUB_PRE = 'PUB_PRE', 'Опубликованная ПредСвязь'
        PUB = 'PUB', 'Опубликованная Связь'

    relation = models.ForeignKey(
        Relation,
        on_delete=models.CASCADE,
        related_name='relation_status',
        verbose_name='Связь'
    )
    status = models.CharField(
        max_length=12,
        choices=Status.choices,
        null=True,
        default=None,
        verbose_name='Статус'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        related_name='user_rel_status',
        verbose_name='Пользователь'
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )
    time_limit = models.IntegerField(
        default=1000,
        verbose_name='Лимит времени'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Текущий статус'
    )

    class Meta:
        verbose_name = 'Статус связи'
        verbose_name_plural = 'Статусы связей'
        ordering = ['status']
