from django.db import models


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
    objects = models.Manager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Вид знания'
        verbose_name_plural = 'Виды знания'
        ordering = ('order', )
