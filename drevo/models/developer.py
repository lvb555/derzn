from django.db import models

class Developer(models.Model):
    """
    Класс для описания таблицы разработчиков
    """
    title = 'Список разработчиков'
    name = models.CharField(
        max_length=128,
        verbose_name='Имя'
    )
    surname = models.CharField(
        max_length=128,
        verbose_name='Фамилия'
    )
    contribution = models.IntegerField(verbose_name='Вклад в проект')
    comment = models.CharField(
        max_length=512,
        verbose_name='Комментарий'
    )
    admin = models.BooleanField(
        default=False,
        verbose_name='Администратор?'
    )

    class Meta:
        verbose_name = 'Разработчика'
        verbose_name_plural = 'Список разработчиков'