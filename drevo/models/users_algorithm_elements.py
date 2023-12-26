from django.db import models
from drevo.models.algorithms_data import AlgorithmWork
from users.models import User
from drevo.models import Znanie


class AlgorithmAdditionalElements(models.Model):
    """
    Таблица для хранения пользовательских элементов алгоритма
    """

    TYPE_CHOICES = [
        ('necessary', 'Состав обязательный'),
        ('unnecessary', 'Состав желательный'),
    ]

    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE)
    algorithm = models.ForeignKey(Znanie, verbose_name='Алгоритм', related_name='changed_algorithm',
                                  on_delete=models.CASCADE, limit_choices_to={'tz__name': 'Алгоритм'})
    work = models.ForeignKey(AlgorithmWork, verbose_name='Работа', on_delete=models.CASCADE)
    parent_element = models.ForeignKey(Znanie, verbose_name='Базовое знание', related_name='bz_element',
                                       on_delete=models.CASCADE)
    element_name = models.CharField(max_length=255, verbose_name='Элемент')
    relation_type = models.CharField(max_length=255, verbose_name='Вид связи', choices=TYPE_CHOICES)
    insertion_type = models.BooleanField(default=False, verbose_name='По связи "Далее"?')

    class Meta:
        verbose_name = 'Пользовательский элемент алгоритма'
        verbose_name_plural = 'Пользовательские элементы алгоритмов'

    def __str__(self):
        return f'{self.user} - {self.work}'
