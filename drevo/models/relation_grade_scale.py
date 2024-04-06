from django.db import models


class RelationGradeScale(models.Model):
    name = models.CharField(
        max_length=80,
        unique=True,
        verbose_name='Наименование оценки',
    )
    low_value = models.FloatField(
        default=0.0,
        verbose_name='Нижнее значение',
    )
    is_low_in_range = models.BooleanField(
        default=False,
        verbose_name='Диапазон включает нижнее значение',
    )
    high_value = models.FloatField(
        default=0.0,
        verbose_name='Верхнее значение',
    )
    is_high_in_range = models.BooleanField(
        default=False,
        verbose_name='Диапазон включает верхнее значение',
    )
    order = models.IntegerField(
        default=1,
        verbose_name="Порядок",
    )

    class Meta:
        verbose_name = 'Градация'
        verbose_name_plural = 'Шкала оценок связей'
        ordering = ('order',)

    def __str__(self):
        return self.name

    def get_base_grade(self) -> float:
        """ Оценка связи в форме числа """

        # откуда здесь такое условие ????
        # return (self.low_value + self.high_value) / 2 if self.low_value != 2.0 else None

        return (self.low_value + self.high_value) / 2

    @classmethod
    def get_grade_object(cls, grade_value) -> 'RelationGradeScale':
        """
        Возвращает объект шкалы оценок связи,
        в диапазон которой входит grade_value.

        По умолчанию возвращает последний (с наименьшим значением)
        """
        if grade_value is None:
            return cls.get_default_grade()

        queryset = cls.objects.all().order_by('order')
        for obj in queryset:
            if obj.low_value < grade_value < obj.high_value:
                return obj
            elif obj.is_low_in_range and obj.low_value == grade_value:
                return obj
            elif obj.is_high_in_range and obj.high_value == grade_value:
                return obj
        return queryset.last()

    @classmethod
    def get_default_grade(cls) -> 'RelationGradeScale':
        """ Оценка по умолчанию"""
        # берем оценку максимально близкую к 1
        return cls.get_grade_object(1)

    def is_hidden(self) -> bool:
        """ Признак скрытия (системности) оценки
            По хорошему надо иметь поле в модели
        """
        return False
