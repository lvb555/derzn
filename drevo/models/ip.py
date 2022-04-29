from django.db import models


class IP(models.Model):
    """
    IP пользавателей
    """
    title = 'IP'
    visits = models.ManyToManyField('Znanie',
                                    verbose_name='ID',
                                    blank=True
                                    )
    ip = models.CharField(max_length=100)
    objects = models.Manager()
