from django.db import models
from users.models import User
from drevo.models import Znanie


class AlgorithmWork(models.Model):
    """
    Таблица для хранения работ по алгоритмам
    """
    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE)
    algorithm = models.ForeignKey(Znanie, verbose_name='Алгоритм', on_delete=models.CASCADE)
    work_name = models.CharField(max_length=255, verbose_name='Работа')

    class Meta:
        verbose_name = 'Работа по алгоритму'
        verbose_name_plural = 'Работы по алгоритмам'

    def __str__(self):
        return f'{self.user} - {self.work_name}'


class AlgorithmData(models.Model):
    """
    Таблица для хранения данных алгоритмов
    """

    TYPE_CHOICES = [
        ('active', 'Активный'),
        ('completed', 'Завершенный'),
        ('available', 'Доступный'),
    ]

    algorithm = models.ForeignKey(Znanie, verbose_name='Алгоритм', related_name='passed_algorithm',
                                  on_delete=models.CASCADE)
    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE)
    element = models.CharField(max_length=255, verbose_name='Элемент')
    element_type = models.CharField(max_length=255, verbose_name='Тип элемента', choices=TYPE_CHOICES)
    work = models.ForeignKey(AlgorithmWork, verbose_name='Работа', on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = 'Данные алгоритма'
        verbose_name_plural = 'Данные алгоритмов'

    def __str__(self):
        return f'{self.user} - {self.work}'
