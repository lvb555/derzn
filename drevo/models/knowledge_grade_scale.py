from django.db import models


class KnowledgeGradeScale(models.Model):
    name = models.CharField(
        max_length=80,
        unique=True,
        verbose_name='Наименование оценки',
    )
    low_value = models.FloatField(verbose_name='Нижнее значение')
    high_value = models.FloatField(verbose_name='Верхнее значение')
    is_high_in_range = models.BooleanField(
        default=False,
        verbose_name='Диапазон включает верхнее значение',
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Градация'
        verbose_name_plural = 'Шкала оценок знаний'
        ordering = ('-high_value',)
