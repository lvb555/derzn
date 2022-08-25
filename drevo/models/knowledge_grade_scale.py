from django.db import models


class KnowledgeGradeScale(models.Model):
    name = models.CharField(
        max_length=80,
        unique=True,
        verbose_name='Наименование оценки',
    )
    low_value = models.FloatField(verbose_name='Нижнее значение')
    is_low_in_range = models.BooleanField(
        default=False,
        verbose_name='Диапазон включает нижнее значение',
    )
    high_value = models.FloatField(verbose_name='Верхнее значение')
    is_high_in_range = models.BooleanField(
        default=False,
        verbose_name='Диапазон включает верхнее значение',
    )

    class Meta:
        verbose_name = 'Градация'
        verbose_name_plural = 'Шкала оценок знаний'
        ordering = ('-high_value',)

    def __str__(self):
        return self.name

    def get_base_grade(self):
        """ Оценка знания в форме числа """

        return (self.low_value + self.high_value) / 2

    @classmethod
    def get_grade_object(cls, grade_value):
        """
        Возвращает объект шкалы оценок знания,
        в диапазон которой входит grade_value.

        По умолчанию возвращает последний (с наименьшим значением)
        """

        queryset = cls.objects.all()
        for obj in queryset:
            if obj.low_value < grade_value < obj.high_value:
                return obj
            elif obj.is_low_in_range and obj.low_value == grade_value:
                return obj
            elif obj.is_high_in_range and obj.high_value == grade_value:
                return obj
        return queryset.last()
