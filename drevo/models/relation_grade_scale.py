from django.db import models


class RelationGradeScale(models.Model):
    _queryset = None
    _default_grade = None

    name = models.CharField(
        max_length=80,
        unique=True,
        verbose_name="Наименование оценки",
    )
    low_value = models.FloatField(
        default=0.0,
        verbose_name="Нижнее значение",
    )
    is_low_in_range = models.BooleanField(
        default=False,
        verbose_name="Диапазон включает нижнее значение",
    )
    high_value = models.FloatField(
        default=0.0,
        verbose_name="Верхнее значение",
    )
    is_high_in_range = models.BooleanField(
        default=False,
        verbose_name="Диапазон включает верхнее значение",
    )
    order = models.IntegerField(
        default=1,
        verbose_name="Порядок",
    )

    class Meta:
        verbose_name = "Градация"
        verbose_name_plural = "Шкала оценок связей"
        ordering = ("order",)

    def __str__(self):
        return self.name

    def get_base_grade(self) -> float:
        """Оценка связи в форме числа"""

        # откуда здесь такое условие ????
        # return (self.low_value + self.high_value) / 2 if self.low_value != 2.0 else None

        return (self.low_value + self.high_value) / 2

    @classmethod
    def get_grade_object(cls, grade_value, use_cache=False) -> "RelationGradeScale":
        """
        Возвращает объект шкалы оценок связи,
        в диапазон которой входит grade_value.

        Если ничего не подходит - вернет последний элемент по порядку order
        """
        if grade_value is None:
            return cls.get_default_grade()

        if not use_cache:
            cls.validate_cache()
        else:
            cls.get_cache()

        for obj in cls._queryset:
            if obj.low_value < grade_value < obj.high_value:
                return obj
            elif obj.is_low_in_range and obj.low_value == grade_value:
                return obj
            elif obj.is_high_in_range and obj.high_value == grade_value:
                return obj
        return cls._queryset.last()

    @classmethod
    def validate_cache(cls):
        cls._queryset = cls.objects.all().order_by("order")
        cls._default_grade = None

    @classmethod
    def get_cache(cls):
        if not cls._queryset:
            cls.validate_cache()
        return cls._queryset

    @classmethod
    def get_default_grade(cls) -> "RelationGradeScale":
        """Оценка по умолчанию"""
        # берем первую оценку по порядку
        if not cls._default_grade:
            cls._default_grade = cls.get_cache().first()
        return cls._default_grade

    def is_hidden(self) -> bool:
        """Признак скрытия (системности) оценки
        По хорошему надо иметь поле в модели
        """
        return False
