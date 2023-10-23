from django.db import models

class GlossaryCategories(models.Model):
    """
    Класс для классификаций терминов глоссария 
    """

    title = "Категорий терминов глоссария"
    name = models.CharField(
        max_length=100,
        verbose_name='Категория',
        unique=True
    )
    order = models.PositiveIntegerField(
        verbose_name='Порядок',
        null=True,
        blank=True
    )
    objects = models.Manager()

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Категорий терминов глоссария',
        verbose_name_plural = 'Категорий терминов глоссария'
        ordering = ('order', )