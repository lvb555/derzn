from django.db import models
from drevo.models import Var


class Turple(models.Model):
    """
        объект Справочник в сервисе созданя документов
    """
    name = models.CharField(max_length=255, verbose_name="Название")
    weight = models.IntegerField(default=100, verbose_name="Порядок")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Справочник'
        verbose_name_plural = 'Справочники'
        ordering = ('weight',)
