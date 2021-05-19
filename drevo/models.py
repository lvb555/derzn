from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from django.urls import reverse
from django.contrib.auth.models import User



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
    content = models.TextField(max_length=512,
                               blank=True,
                               null=True,
                               verbose_name='Содержание'
                               )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('drevo_type', kwargs = {"pk": self.pk})

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    class MPTTMeta:
        order_insertion_by = ['name']


class Tz(models.Model):
    """
    Виды знания
    """
    title = 'Вид знания'
    name = models.CharField(max_length=128,
                            unique=True,
                            verbose_name='Название')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Вид знания'
        verbose_name_plural = 'Виды знания'


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
    category = models.ForeignKey(Category,
                           on_delete=models.PROTECT,
                           verbose_name='Категория',
                           null=True,
                           blank=True
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
    href = models.URLField(max_length=256,
                           verbose_name='Источник',
                           help_text='укажите www-адрес источника',
                           null=True,
                           blank=True)
    source_com = models.CharField(max_length=256,
                                  verbose_name='Комментарий к источнику',
                                  null=True,
                                  blank=True
                                  )
    author = models.ForeignKey(Author,
                               on_delete=models.PROTECT,
                               verbose_name='Автор',
                               help_text='укажите автора'
                               )
    date = models.DateField(auto_now_add=True,
                            verbose_name='Дата создания',
                            )
    user = models.ForeignKey(User,
                               on_delete=models.PROTECT,
                               editable=False,
                               verbose_name='Пользователь'
                               )
    order = models.IntegerField(verbose_name='Порядок',
                                help_text='укажите порядковый номер')

    is_published = models.BooleanField(default=False,
                                       verbose_name='Опубликовано?'
                                       )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Знание'
        verbose_name_plural = 'Знания'
        ordering = ('order', )


class Tr(models.Model):
    """
    Виды связей
    """
    title = 'Вид связи'
    name = models.CharField(max_length=256,
                            verbose_name='Название',
                            unique=True
                            )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Вид связи'
        verbose_name_plural = 'Виды связи'
        ordering = ('name', )


class Relation(models.Model):
    """
    Класс для связи Знание-Знание
    """
    title = 'Связь'
    # связанное знание
    bz = models.ForeignKey(Znanie,
                           on_delete=models.PROTECT,
                           verbose_name='Базовое знание',
                           help_text='укажите базовое знание',
                           related_name = 'base'
                           )
    tr = models.ForeignKey(Tr,
                           on_delete=models.PROTECT,
                           verbose_name='Вид связи',
                           help_text='укажите вид связи'
                           )
    rz = models.ForeignKey(Znanie,
                           on_delete=models.PROTECT,
                           verbose_name='Связанное знание',
                           help_text='укажите связанное знание',
                           related_name='related'
                           )
    author = models.ForeignKey(Author,
                               on_delete=models.PROTECT,
                               verbose_name='Автор',
                               help_text='укажите автора'
                               )
    date = models.DateField(auto_now_add=True,
                            verbose_name='Дата создания',
                            )
    user = models.ForeignKey(User,
                               on_delete=models.PROTECT,
                               editable=False,
                               verbose_name='Пользователь'
                               )

    def __str__(self):
        return f"{self.title} {self.bz.pk}-{self.bz}-{self.rz.pk}"

    class Meta:
        verbose_name = 'Связь'
        verbose_name_plural = 'Связи'
        ordering = ('-date', )