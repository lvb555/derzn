from django.db import models
from mptt.models import TreeForeignKey, MPTTModel


class HelpURLTag(models.Model):
    name = models.CharField(
        verbose_name='Название тега',
        max_length=255,
        unique=True,
        blank=True
    )

    class Meta:
        verbose_name = 'URL тег страницы "Помощь"'
        verbose_name_plural = 'URL теги страницы "Помощь"'
        ordering = ['name']

    def __str__(self):
        return self.name


class Help(MPTTModel):
    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name='Название'
    )
    content = models.TextField(
        verbose_name="Содержание",
        blank=True,
        null=True,
    )
    parent = TreeForeignKey(
        verbose_name='Родитель',
        to='self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )
    url_tag = models.ManyToManyField(
        verbose_name="Тег URL",
        to=HelpURLTag,
        related_name='help',
        blank=True,
    )
    is_published = models.BooleanField(
        default=False,
        verbose_name='Опубликовано'
    )
    is_group = models.BooleanField(
        default=False,
        verbose_name='Группа'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Раздел помощь'
        verbose_name_plural = 'Разделы помощи'

    class MPTTMeta:
        order_insertion_by = ['name']
