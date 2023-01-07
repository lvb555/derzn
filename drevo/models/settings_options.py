from django.db import models
from .parameter_categories import ParameterCategories


class SettingsOptions(models.Model):
    name = models.CharField(
        verbose_name='Название параметра',
        max_length=255
    )
    category = models.ForeignKey(
        verbose_name='Категория',
        to=ParameterCategories,
        on_delete=models.CASCADE,
        related_name='params',
        blank=True,
        null=True
    )
    default_param = models.CharField(
        verbose_name='Значение по умолчанию',
        max_length=255
    )
    admin = models.BooleanField(
        verbose_name='Администратор',
        default=False
    )

    class Meta:
        verbose_name = 'Параметр настроек'
        verbose_name_plural = 'Параметры настроек'
        ordering = ['name']

    def __str__(self):
        return self.name
