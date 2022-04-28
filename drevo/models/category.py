from django.db import models
from mptt.models import MPTTModel, TreeForeignKey, TreeManager
from django.urls import reverse
from ..managers import CategoryManager


class Category(MPTTModel):
    """
    Категория (рубрика), к которой относится знание.
    Иерархическая структура.
    """
    title = 'Категория'
    name = models.CharField(max_length=128,
                            unique=True,
                            verbose_name='Название')
    parent = TreeForeignKey('self',
                            on_delete=models.CASCADE,
                            null=True,
                            blank=True,
                            related_name='children'
                            )
    content = models.TextField(max_length=1024,
                               blank=True,
                               null=True,
                               verbose_name='Содержание'
                               )
    is_published = models.BooleanField(default=False,
                                       verbose_name='Опубликовано?'
                                       )
    # менеджеры объектов
    objects = models.Manager()
    tree_objects = TreeManager()
    published = CategoryManager()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('drevo_type', kwargs={"pk": self.pk})

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

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    class MPTTMeta:
        order_insertion_by = ['name']
