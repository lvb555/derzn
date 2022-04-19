from django.db import models


class AuthorType(models.Model):
    """
    Класс для описания вида авторов
    """
    title = 'Вид Автора'
    name = models.CharField(max_length=128,
                            verbose_name='Вид авторов')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Вид авторов'
        verbose_name_plural = 'Виды авторов'
