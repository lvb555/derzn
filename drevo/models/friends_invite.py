from django.db import models

from users.models import User


class FriendsInviteTerm(models.Model):
    """
    реквизит "Отправитель" - указатель на таблицу "Пользователи"
    реквизит "Получатель" - указатель на таблицу "Пользователи"
    реквизит "Принято" - логический: True - принято; False - не принято
    реквизит "Дата отправки" - дата и время
    """
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Отправитель',
        related_name='sender'
    )
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Получатель',
        related_name='recipient'
    )
    accept = models.BooleanField(
        verbose_name='Принято'
    )
    date_added = models.DateField(
        auto_now=True,
        verbose_name='Дата отправки'
    )
