from django.db import models


class RelationGradeScale(models.Model):
    name = models.CharField(
        max_length=80,
        unique=True,
        verbose_name='Наименование оценки',
    )
    value = models.FloatField(verbose_name='Значение')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Градация'
        verbose_name_plural = 'Шкала оценок связей'
        ordering = ('-value',)
