from colorfield.fields import ColorField
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

    argument_color_background = ColorField(
        default="#00CC00",
        verbose_name='Цвет фона довода "За"'
    )
    argument_color_font = ColorField(
        default="#000000",
        verbose_name='Цвет шрифта довода "За"'
    )
    contraargument_color_background = ColorField(
        default="#FD0B33",
        verbose_name='Цвет фона довода "Против"'
    )
    contraargument_color_font = ColorField(
        default="#000000",
        verbose_name='Цвет шрифта довода "Против"'
    )
    order = models.IntegerField(
        default=1,
        verbose_name="Порядок",
    )

    class Meta:
        verbose_name = 'Градация'
        verbose_name_plural = 'Шкала оценок знаний'
        ordering = ('order',)

    def __str__(self):
        return self.name

    def get_base_grade(self):
        """ Оценка знания в форме числа """

        return (self.low_value + self.high_value) / 2 if self.low_value != 2.0 else None

    @classmethod
    def get_grade_object(cls, grade_value):
        """
        Возвращает объект шкалы оценок знания,
        в диапазон которой входит grade_value.

        По умолчанию возвращает последний (с наименьшим значением)
        """
        if grade_value is None:
            return None

        queryset = cls.objects.all().order_by('order')
        for obj in queryset:
            if obj.low_value < grade_value < obj.high_value:
                return obj
            elif obj.is_low_in_range and obj.low_value == grade_value:
                return obj
            elif obj.is_high_in_range and obj.high_value == grade_value:
                return obj
        return queryset.last()
