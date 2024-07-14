from django.db import models
from mptt.fields import TreeForeignKey
from mptt.managers import TreeManager
from mptt.models import MPTTModel

from users.models import User
from drevo.models import Znanie


class StatusType(models.Model):
    """
    Виды статусов страниц
    """
    name = models.CharField(max_length=128, unique=True, verbose_name='Название статуса')
    text_for_users = models.CharField(max_length=128, verbose_name='Текст для пользователя')

    objects = models.Manager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Вид статуса страниц'
        verbose_name_plural = 'Виды статусов страниц'


class SitePage(MPTTModel):
    """
    Страницы сайта
    """
    TYPE_CHOICES = [
        ('group', 'Группа'),
        ('page', 'Страница'),
        ('type_of_complicated_knowledge', 'Вид сложного знания'),
        ('complicated_knowledge', 'Сложное знание'),
        ('label', 'Ярлык')
    ]

    page = models.ForeignKey(Znanie, verbose_name='Страница', on_delete=models.CASCADE, null=True, blank=True)
    parent = TreeForeignKey(verbose_name='Родитель', to='self', on_delete=models.CASCADE, null=True, blank=True,
                            related_name='children')
    type = models.CharField(max_length=255, verbose_name='Тип', choices=TYPE_CHOICES)
    base_page = TreeForeignKey(verbose_name='Базовая страница', to='self', on_delete=models.CASCADE, null=True,
                               blank=True, related_name='links')
    functional = models.BooleanField(default=False, verbose_name='Функционал')
    design_needed = models.BooleanField(default=False, verbose_name='Необходимость макета')
    design = models.BooleanField(default=False, verbose_name='Макет')
    layout = models.BooleanField(default=False, verbose_name='Верстка')
    help_page = models.BooleanField(default=False, verbose_name='Страница помощи')
    help_page_content = models.BooleanField(default=False, verbose_name='Контент помощи')
    notification = models.BooleanField(default=False, verbose_name='Оповещение')
    status = models.ForeignKey(StatusType, verbose_name='Статус', on_delete=models.PROTECT, null=True, blank=True)
    link = models.URLField(max_length=256, verbose_name='URL-адрес', null=True, blank=True)
    subscribers = models.ManyToManyField('users.User', verbose_name='Подписчики', blank=True)
    order = models.IntegerField(verbose_name='Порядок', null=True, blank=True)

    objects = models.Manager()
    tree_objects = TreeManager()

    def __str__(self):
        return self.page.name if self.page else 'Ярлык'

    class Meta:
        verbose_name = 'Страница сайта'
        verbose_name_plural = 'Страницы сайта'

    class MPTTMeta:
        order_insertion_by = ['order']


class PageHistory(models.Model):
    """
    История изменений страниц
    """
    PROP_CHOICES = [
        ('parent', 'Родитель'),
        ('type', 'Тип'),
        ('base_page', 'Базовая страница'),
        ('functional', 'Функционал'),
        ('design_needed', 'Необходимость макета'),
        ('design', 'Макет'),
        ('layout', 'Верстка'),
        ('help_page', 'Страница помощи'),
        ('help_page_content', 'Контент помощи'),
        ('notification', 'Оповещение'),
        ('status', 'Статус'),
        ('link', 'URL-адрес'),
        ('subscribers', 'Подписчики'),
        ('order', 'Порядок')
    ]

    page = models.ForeignKey(SitePage, verbose_name='Страница', on_delete=models.CASCADE)
    prop = models.CharField(max_length=255, verbose_name='Реквизиты', choices=PROP_CHOICES)
    previous_value = models.CharField(max_length=256, verbose_name='Предыдущее значение', null=True)
    last_value = models.CharField(max_length=256, verbose_name='Последнее значение', null=True)
    staff_member = models.ForeignKey(User, on_delete=models.PROTECT, null=True, verbose_name='Сотрудник')
    date = models.DateTimeField(auto_now_add=True, verbose_name='Дата')

    objects = models.Manager()

    def __str__(self):
        return f'{self.page}-{self.date}'

    class Meta:
        verbose_name = 'История изменения страницы'
        verbose_name_plural = 'История изменений страниц'
