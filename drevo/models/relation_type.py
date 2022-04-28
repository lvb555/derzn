from django.db import models


class Tr(models.Model):
    """
    Виды связей
    """
    title = 'Вид связи'
    name = models.CharField(max_length=256,
                            verbose_name='Название',
                            unique=True
                            )
    order = models.PositiveSmallIntegerField(
        verbose_name='Порядок',
        help_text='укажите порядковый номер',
        default=0,
    )
    is_systemic = models.BooleanField(default=False,
                                      verbose_name='Системный?')

    objects = models.Manager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Вид связи'
        verbose_name_plural = 'Виды связи'
        ordering = ('order', 'name',)
