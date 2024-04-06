from colorfield.fields import ColorField
from django.db import models


class KnowledgeGradeScale(models.Model):
    name = models.CharField(
        max_length=80,
        unique=True,
        verbose_name="Наименование оценки",
    )
    low_value = models.FloatField(verbose_name="Нижнее значение")
    is_low_in_range = models.BooleanField(
        default=False,
        verbose_name="Диапазон включает нижнее значение",
    )
    high_value = models.FloatField(verbose_name="Верхнее значение")
    is_high_in_range = models.BooleanField(
        default=False,
        verbose_name="Диапазон включает верхнее значение",
    )

    argument_color_background = ColorField(default="#00CC00", verbose_name='Цвет фона довода "За"')
    argument_color_font = ColorField(default="#000000", verbose_name='Цвет шрифта довода "За"')
    contraargument_color_background = ColorField(default="#FD0B33", verbose_name='Цвет фона довода "Против"')
    contraargument_color_font = ColorField(default="#000000", verbose_name='Цвет шрифта довода "Против"')
    order = models.IntegerField(
        default=1,
        verbose_name="Порядок",
    )

    class Meta:
        verbose_name = "Градация"
        verbose_name_plural = "Шкала оценок знаний"
        ordering = ("order",)

    def __str__(self):
        return self.name

    def get_base_grade(self) -> float:
        """Оценка знания в форме числа"""

        # откуда здесь такое условие ?????
        # return (self.low_value + self.high_value) / 2 if self.low_value != 2.0 else None
        return (self.low_value + self.high_value) / 2

    @classmethod
    def get_grade_object(cls, grade_value) -> "KnowledgeGradeScale":
        """
        Возвращает объект шкалы оценок знания,
        в диапазон которой входит grade_value.

        Если ничего не подходит - вернет последний элемент по порядку order
        """
        if grade_value is None:
            return cls.get_default_grade()

        queryset = cls.objects.all().order_by("order")

        for obj in queryset:
            if obj.low_value < grade_value < obj.high_value:
                return obj
            elif obj.is_low_in_range and obj.low_value == grade_value:
                return obj
            elif obj.is_high_in_range and obj.high_value == grade_value:
                return obj
        return queryset.last()

    @classmethod
    def get_default_grade(cls):
        """Оценка по умолчанию"""
        # берем оценку максимально близкую к 0
        return cls.get_grade_object(0)

    def is_hidden(self) -> bool:
        """Признак скрытия (системности) оценки
        в шкале оно есть, а выбрать из списка и присвоить нельзя
        По-хорошему надо иметь поле в модели!
        """
        return self.name == "Нет оценки"
