from django.db import models
from users.models import User


class BrowsingHistory(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        editable=False,
        verbose_name='Пользователь'
    )

    znanie = models.ForeignKey(
        'Znanie',
        on_delete=models.CASCADE,
        verbose_name='Знание',
        editable=False,
    )

    date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата просмотра',
    )

    class Meta:
        verbose_name = 'Просмотр'
        verbose_name_plural = 'Просмотры'
        ordering = ('-date',)

    def __str__(self):
        return f"{self.znanie.name} - {self.date}"
