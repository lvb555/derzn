from django.db import models
from .knowledge import Znanie


class Tz(models.Model):
    """
    Виды знания
    """
    title = 'Вид знания'
    name = models.CharField(max_length=128,
                            unique=True,
                            verbose_name='Название')
    order = models.PositiveSmallIntegerField(
        verbose_name='Порядок',
        help_text='укажите порядковый номер',
        default=0,
        blank=True
    )
    is_systemic = models.BooleanField(default=False,
                                      verbose_name='Системный?')

    is_group = models.BooleanField(default=False,
                                   verbose_name='Вид является группой?')

    can_be_rated = models.BooleanField(default=False,
                                       verbose_name='Возможна оценка знания')
    is_send = models.BooleanField(default=True,
                                  verbose_name='Пересылать')
    objects = models.Manager()

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        for obj in Znanie.objects.filter(tz=self).all():
            obj.is_send = self.is_send
            obj.save()
        super(Tz, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Вид знания'
        verbose_name_plural = 'Виды знания'
        ordering = ('order',)
