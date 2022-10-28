from django.db import models

from users.models import User


class FriendsTerm(models.Model):
    """
    реквизит "Пользователь" - указатель на таблицу "Пользователи"
    реквизит "Друг" - указатель на таблицу "Пользователи"
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='users'
    )
    friend = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Друг',
        related_name='friends'
    )

    
    def __str__(self):
        return str(self.user.id) + " - " + str(self.friend.id)

    class Meta:
        verbose_name = 'Дружба'
        verbose_name_plural = 'Друзья'
