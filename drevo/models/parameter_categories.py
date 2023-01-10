from django.db import models


class ParameterCategories(models.Model):
    name = models.CharField(
        verbose_name='Категория',
        max_length=255
    )

    class Meta:
        verbose_name = 'Категория параметра'
        verbose_name_plural = 'Категории параметров'
        ordering = ['name']

    def __str__(self):
        return self.name
