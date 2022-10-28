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


    def __str__(self):
        return str(self.sender) + " -> " + str(self.recipient)


    class Meta:
        verbose_name = 'Заявка в друзья'
        verbose_name_plural = 'Заявки в друзья'
