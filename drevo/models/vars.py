from __future__ import annotations
from django.db import models


class Var(models.Model):

    """
        объект в сервисе создания документов
    """

    available_types_of_content = (
        (0, 'Текст'),
        (1, 'Число'),
        (2, 'Дата'),
        (3, 'Справочник'),
    )

    available_sctructures = (
        (0, 'Переменная'),
        (1, 'Массив'),
        (2, 'Управление')
    )

    types_of_availability = (
        (0, 'Локальный'),
        (1, 'Глобальный'),
        (2, 'Общий')
    )

    name = models.CharField(max_length=50, verbose_name="Имя объекта")
    structure = models.IntegerField(
        default=0,
        choices=available_sctructures,
        verbose_name="Тип объекта")
    is_main = models.BooleanField(default=False, verbose_name="Группа")
    availability = models.IntegerField(
        default=0,
        choices=types_of_availability,
        verbose_name="Класс объекта")
    weight = models.IntegerField(default=1, verbose_name="Порядок")
    fill_title = models.TextField(verbose_name="Обращение", default="", blank=True)
    subscription = models.BooleanField(default=False, verbose_name="Прописью")
    optional = models.BooleanField(default=False, verbose_name="Необязательность")
    type_of = models.IntegerField(
        default=0,
        choices=available_types_of_content,
        verbose_name="Вид значения")
    knowledge = models.ForeignKey(
        to="drevo.Znanie",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Знание")
    connected_to = models.ForeignKey(
        to='drevo.Var',
        on_delete=models.PROTECT,
        verbose_name="Родитель",
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
        ordering = ('weight',)
