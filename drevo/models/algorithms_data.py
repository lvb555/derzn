from django.db import models
from users.models import User
from drevo.models import Znanie


class AlgorithmData(models.Model):
    """
    Таблица для хранения данных алгоритмов
    """

    TYPE_CHOICES = [
        ('active', 'Активный'),
        ('completed', 'Завершенный'),
        ('available', 'Доступный'),
    ]

    algorithm = models.ForeignKey(Znanie, verbose_name='Алгоритм', related_name='passed_algorithm', on_delete=models.CASCADE)
    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE)
    element = models.ForeignKey(Znanie, verbose_name='Элемент', related_name='algorithm_element', on_delete=models.CASCADE)
    element_type = models.CharField(max_length=255, verbose_name='Тип элемента', choices=TYPE_CHOICES)
    work_name = models.CharField(max_length=255, verbose_name='Работа')

    class Meta:
        verbose_name = 'Данные алгоритма'
        verbose_name_plural = 'Данные алгоритмов'

    def __str__(self):
        return f'{self.user} - {self.work_name}'
