from django.db import models


class ChapterDescriptions(models.Model):
    """
    Класс для описания глав страницы "О проекте"
    """
    
    title = 'Глава описания'
    name = models.CharField(
        max_length=255,
        verbose_name='Название главы',
        unique=True
    )
    content = models.TextField(
        max_length=2048,
        blank=True,
        null=True,
        verbose_name='Содержание'
    )
    order = models.PositiveIntegerField(
        verbose_name='Порядок',
        help_text='Укажите порядковый номер',
        null=True,
        blank=True
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Глава описания'
        verbose_name_plural = 'Главы описания'
        ordering = ('order',)
