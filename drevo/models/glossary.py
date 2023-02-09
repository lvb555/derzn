from django.db import models


class GlossaryTerm(models.Model):
    """
    Класс для описания термина глоссария
    """
    title = 'Термин глоссария'
    order = models.PositiveIntegerField(
        verbose_name='Порядок',
        help_text='Укажите порядковый номер',
        null=True,
        blank=True
    )
    name = models.CharField(
        max_length=255,
        verbose_name='Термин',
        unique=True
    )
    description = models.TextField(
        max_length=2048,
        blank=True,
        null=True,
        verbose_name='Описание'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата и время создания',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата и время редактирования',
    )

    is_published = models.BooleanField(
        default=True,
        verbose_name='Опубликовано?'
    )
    objects = models.Manager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Термин глоссария'
        verbose_name_plural = 'Термины глоссария'
        ordering = ('order', 'name', )
