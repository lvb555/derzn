from django.db import models
from users.models import User


class ZnRating(models.Model):
    LIKE = 'like'
    DISLIKE = 'dislike'
    BLANK = ''

    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             verbose_name='Пользователь'
                             )
    znanie = models.ForeignKey('Znanie',
                               on_delete=models.CASCADE,
                               verbose_name='Знание'
                               )
    value = models.CharField(max_length=7,
                             blank=True,
                             verbose_name='Значение'
                             )
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name='Дата и время создания',
                                      )
    updated_at = models.DateTimeField(auto_now=True,
                                      verbose_name='Дата и время изменения',
                                      )

    class Meta:
        verbose_name = 'Рейтинг знаний'
        verbose_name_plural = 'Рейтинг знаний'
        unique_together = ('user', 'znanie')
