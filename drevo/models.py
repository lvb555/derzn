from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from django.urls import reverse


class Author(models.Model):
    """
    Класс для описания авторов
    """
    title = 'Автор'
    name = models.CharField(max_length=128,
                            verbose_name='Имя')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Автор'
        verbose_name_plural = 'Авторы'


class Tz(MPTTModel):
    """
    Виды знания
    """
    title = 'Вид знания'
    name = models.CharField(max_length=128,
                            unique=True,
                            verbose_name='Название')
    parent = TreeForeignKey('self',
                            on_delete=models.CASCADE,
                            null=True,
                            blank=True,
                            related_name='children'
                            )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('drevo_type', kwargs = {"pk": self.pk})

    class Meta:
        verbose_name = 'Вид знания'
        verbose_name_plural = 'Виды знания'

    class MPTTMeta:
        order_insertion_by = ['name']


class Label(models.Model):
    """
    Метки
    """
    title = 'Метка'
    name = models.CharField(max_length=128,
                            unique=True,
                            verbose_name='Название')

    def __str__(self):
        return self.name

    class MPTTMeta:
        order_insertion_by=['name']

    class Meta:
        verbose_name = 'Метка'
        verbose_name_plural = 'Метки'


class Znanie(models.Model):
    """
    Класс для описания сущности 'Знание'
    """
    title = 'Знание'
    name = models.CharField(max_length=256,
                            verbose_name='Тема',
                            unique=True
                            )
    tz = models.ForeignKey(Tz,
                           on_delete=models.PROTECT,
                           verbose_name='Вид знания'
                           )
    content = models.TextField(max_length=512,
                               blank=True,
                               null=True,
                               verbose_name='Содержание'
                               )
    href = models.URLField(verbose_name='Источник',
                           help_text='укажите www-адрес источника')
    source_com = models.CharField(max_length=128,
                                  verbose_name='Комментарий к источнику'
                                  )
    author = models.ForeignKey(Author,
                               on_delete=models.PROTECT,
                               verbose_name='Автор',
                               help_text='укажите автора'
                               )
    date = models.DateField(auto_now=True,
                            verbose_name='Дата создания',
                            )

    # связанное знание
    rz = models.ForeignKey('self',
                           on_delete=models.PROTECT,
                           verbose_name='Связанное знание',
                           help_text='укажите связанное знание',
                           blank=True,
                           null=True
                           )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Знание'
        verbose_name_plural = 'Знания'
        ordering = ('name', )
