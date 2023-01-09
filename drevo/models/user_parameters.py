from django.db import models
from .settings_options import SettingsOptions


class UserParameters(models.Model):
    user = models.ForeignKey(
        verbose_name='Пользователь',
        to='users.User',
        on_delete=models.CASCADE,
        related_name='user_params'
    )
    param = models.ForeignKey(
        verbose_name='Параметр',
        to=SettingsOptions,
        on_delete=models.CASCADE,
        related_name='user_params'
    )
    param_value = models.CharField(
        verbose_name='Значение параметра',
        max_length=255,
        blank=True
    )

    class Meta:
        verbose_name = 'Параметр пользователя'
        verbose_name_plural = 'Параметры пользователя'
        ordering = ['param']

    def __str__(self):
        return f'{self.param}'
