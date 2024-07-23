from turtle import mode
from django.db import models


class TurpleElement(models.Model):
    """
        объект Элемент справочника в сервисе создания документов
    """

    value = models.CharField(max_length=255, verbose_name="Содержание")
    turple = models.ForeignKey(
        to='drevo.Turple',
        on_delete=models.CASCADE,
        verbose_name="Справочник")
    weight = models.IntegerField(default=1, verbose_name="Порядок")
    object = models.ForeignKey('Turple',
                               on_delete=models.CASCADE,
                               verbose_name='Объект',
                               related_name='tuple_elements',
                               null=True)

    class Meta:
        verbose_name = 'Элемент справочника'
        verbose_name_plural = 'Элементы справочника'
        ordering = ('weight',)
