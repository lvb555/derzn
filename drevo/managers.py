from django.db import models


class ZManager(models.Manager):
    """
    Manager записей для сущности Znanie.
    Установлены фильтр и сортировка.
    """

    def get_queryset(self):
        return super().get_queryset().filter(is_published=True).order_by("category")


class CategoryManager(models.Manager):
    """
    Manager записей для сущности Category.
    Установлены фильтр по полю публикации.
    """

    def get_queryset(self):
        return super().get_queryset().filter(is_published=True)
