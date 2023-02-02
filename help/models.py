from django.db import models
from django.urls import reverse
from mptt.managers import TreeManager
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
        blank=True
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

    objects = models.Manager()
    tree_objects = TreeManager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Раздел помощь'
        verbose_name_plural = 'Разделы помощи'

    def get_absolute_url(self):
        return reverse('help', kwargs={"pk": self.pk})

    def has_published_children(self) -> bool():
        """
        Возвращает True, если среди потомков объекта имеются опубликованные,
        False в противном случае.
        """
        children = self.get_children()
        for child in children:
            if child.is_published:
                return True
        return False

    class MPTTMeta:
        order_insertion_by = ['name']
