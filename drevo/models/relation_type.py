from django.db import models


class Tr(models.Model):
    """
    Виды связей
    """

    FOR = False
    AGAINST = True

    ARGUMENT_TYPES = (
        (FOR, 'За'),
        (AGAINST, 'Против'),
    )

    title = 'Вид связи'
    name = models.CharField(max_length=255,
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
    is_argument = models.BooleanField(default=False,
                                      verbose_name='Доказательная связь')
    argument_type = models.BooleanField(choices=ARGUMENT_TYPES,
                                        default=FOR,
                                        verbose_name='Тип довода')
    has_invert = models.BooleanField(editable=False,
                                     verbose_name='Доступна инверсия')
    invert_tr = models.ForeignKey('self',
                                  blank=True,
                                  null=True,
                                  on_delete=models.CASCADE,
                                  related_name='invert_relation',
                                  verbose_name='Инверсия',
                                  help_text='Только для инверсивных связей')

    objects = models.Manager()

    def clean(self):
        self.has_invert = False
        if self.invert_tr is not None:
            self.has_invert = True

    class Meta:
        verbose_name = 'Вид связи'
        verbose_name_plural = 'Виды связи'
        ordering = ('order', 'name',)

    def __str__(self):
        return self.name
