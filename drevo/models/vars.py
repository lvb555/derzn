from __future__ import annotations
from django.db import models
from django.forms.models import model_to_dict
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator


class Var(models.Model):

    """
        объект Переменная в сервисе создания документов
    """

    available_types_of_content = (
        (0, 'Текст'),
        (1, 'Число'),
        (2, 'Дата')
    )

    available_sctructures = (
        (0, 'Переменная'),
        (1, 'Массив'),
        (2, 'Справочник'),
        (3, 'Итератор'),
        (4, 'Условие'),
    )

    name = models.CharField(max_length=50, verbose_name="Имя объекта")
    structure = models.IntegerField(
        default=0, 
        choices=available_sctructures,
        verbose_name="Структура")
    is_main = models.BooleanField(default=False, verbose_name="Главная")
    is_global = models.BooleanField(default=False, verbose_name="Глобальная")
    weight = models.IntegerField(default=100, verbose_name="Порядок")
    fill_title = models.TextField(verbose_name="Обращение", default="", blank=True)
    subscription = models.BooleanField(default=False, verbose_name="Прописью")
    optional = models.BooleanField(default=False, verbose_name="Необязательность")
    type_of = models.IntegerField(
        default=0, 
        choices=available_types_of_content,
        verbose_name="Тип")
    knowledge = models.ForeignKey(
        to="drevo.Znanie", 
        on_delete=models.CASCADE, 
        verbose_name="Знание")
    connected_to = models.ForeignKey(
        to='drevo.Var', 
        on_delete=models.PROTECT, 
        verbose_name="Подчинение", 
        null=True, 
        blank=True)
    turple = models.ForeignKey(
        to="drevo.Turple", 
        null=True,
        blank=True,
        on_delete=models.CASCADE, 
        verbose_name="Справочник")
    comment = models.CharField(
        max_length=255, 
        default='', 
        blank=True, 
        verbose_name="Комментарий")

    def __str__(self):
        return self.name


    class Meta:
        verbose_name = "Объект"
        verbose_name_plural = "Объекты шаблонов"
