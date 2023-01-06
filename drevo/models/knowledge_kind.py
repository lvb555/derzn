from django.db import models
from .knowledge import Znanie


class Tz(models.Model):
    """
    Виды знания
    """
    title = 'Вид знания'
    name = models.CharField(
        max_length=128,
        unique=True,
        verbose_name='Название'
    )
    order = models.PositiveSmallIntegerField(
        verbose_name='Порядок',
        help_text='укажите порядковый номер',
        default=0,
        blank=True
    )
    is_systemic = models.BooleanField(
        default=False,
        verbose_name='Системный?'
    )

    is_group = models.BooleanField(
        default=False,
        verbose_name='Вид является группой?'
    )

    can_be_rated = models.BooleanField(
        default=False,
        verbose_name='Возможна оценка знания'
    )
    is_send = models.BooleanField(
        default=True,
        verbose_name='Пересылать'
    )
    is_author_required = models.BooleanField(
        default=False,
        verbose_name='Автор обязателен для заполнения?'
    )
    is_href_required = models.BooleanField(
        default=False,
        verbose_name='Источник обязателен для заполнения?'
    )
    objects = models.Manager()

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        znaniya = Znanie.objects.filter(tz=self).all()
        for znanie in znaniya:
            znanie.is_send = self.is_send
        Znanie.objects.bulk_update(znaniya, ['is_send'])
        super(Tz, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Вид знания'
        verbose_name_plural = 'Виды знания'
        ordering = ('order',)
