from django.db import models
from drevo.models import Var


class Turple(models.Model):
    """
        объект Справочник в сервисе созданя документов
    """

    knowledge = models.ForeignKey(
        to='drevo.Znanie',
        on_delete=models.CASCADE,
        verbose_name="Знание")

    name = models.CharField(max_length=255, verbose_name="Название")
    availability = models.IntegerField(
        default=0,
        choices=Var.types_of_availability,
        verbose_name="Доступность")
    weight = models.IntegerField(default=100, verbose_name="Порядок")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Справочник'
        verbose_name_plural = 'Справочники'
        ordering = ('weight',)
