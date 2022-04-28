from django.db import models


class Label(models.Model):
    """
    Метки
    """
    title = 'Метка'
    name = models.CharField(max_length=128,
                            unique=True,
                            verbose_name='Название')

    objects = models.Manager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Метка'
        verbose_name_plural = 'Метки'
        ordering = ('name',)
