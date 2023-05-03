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
    name = models.CharField(
        max_length=128,
        unique=True,
        verbose_name='Название'
    )
    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )
    content = models.TextField(
        max_length=1024,
        blank=True,
        null=True,
        verbose_name='Содержание'
    )
    subscribers = models.ManyToManyField(
        'users.User',
        blank=True
    )
    is_published = models.BooleanField(
        default=False,
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

    def get_experts(self):
        """
        Возвращает QuerySet с экспертами в данной категории
        """
        return self.category_list.select_related()

    def get_expert_ancestors_category(self):
        """Возвращает список экспертов по данной категории и предками данной категории"""
        categories = self.get_ancestors(ascending=False, include_self=True)
        expert_list = []
        for category in categories:
            experts = category.get_experts()
            if not experts:
                continue
            for expert in experts:
                expert_list.append(expert.expert)
        return expert_list

    def get_admins(self):
        """
        Возвращает QuerySet с руководителями в данной категории
        """
        return self.special_permissions.select_related()

    def get_admin_ancestors_category(self):
        """Возвращает список руководителей по данной категории и предками данной категории"""
        categories = self.get_ancestors(ascending=False, include_self=True)
        admin_list = []
        for category in categories:
            admins = category.get_admins()
            if not admins:
                continue
            for admin in admins:
                admin_list.append(admin.expert)
        return admin_list

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    class MPTTMeta:
        order_insertion_by = ['name']
