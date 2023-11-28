from __future__ import annotations
from django.db import models
from django.core.exceptions import ValidationError

class Var(models.Model):
    knowledge = models.ForeignKey(to="drevo.Znanie", on_delete=models.CASCADE, verbose_name="Знание")
    name = models.CharField(max_length=50, verbose_name="Имя")
    is_array = models.BooleanField(default=False, verbose_name="Массив")
    is_main = models.BooleanField(default=False, verbose_name="Главная")
    is_global = models.BooleanField(default=False, verbose_name="Глобальная")
    weight = models.IntegerField(verbose_name="Порядок")
    connected_to = models.ForeignKey(to='drevo.Var', on_delete=models.PROTECT, verbose_name="Подчинение", default=None)

    def __str__(self):
        return self.name

    def clean(self):
        if Var.objects.filter(knowledge=self.knowledge, name=self.name).count() != 0:
            raise ValidationError(f'Переменная с именем {self.name} уже существует в контексте этого документа')

    class Meta:
        verbose_name = "Переменная"
        verbose_name_plural = "Переменные"
