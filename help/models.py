from django.db import models
from mptt.models import TreeForeignKey, MPTTModel
from django.urls import reverse


class CategoryHelp(MPTTModel):
    title = 'Категории раздела помощь'
    name = models.CharField(max_length=100,
                            unique=True,
                            verbose_name='Название')
    description = models.CharField(max_length=200,
                                   verbose_name='Описание категории')
    parent = TreeForeignKey('self',
                            on_delete=models.CASCADE,
                            null=True, blank=True,
                            related_name='children')
    url_tag = models.CharField(max_length=20,
                               unique=True,
                               blank=True,
                               verbose_name="URL тег адреса",)
    is_published = models.BooleanField(default=False,
                                       verbose_name='Опубликовано?'
                                       )

    def save(self, *args, **kwargs):
        """
        Добавляет перед url_tag символ "/", если его нет.
        Убирает символ "/" в конце url_tag, если он есть.
        """
        if len(self.url_tag) == 0 or self.url_tag[0] != '/':
            self.url_tag = '/' + self.url_tag
        if len(self.url_tag) >= 2 and self.url_tag[-1] == '/':
            self.url_tag = self.url_tag[:-1]

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        try:
            tag = self.url_tag.strip()
            return reverse('help', args=[str(tag)[1:]])
        except Exception:
            return reverse('help')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Категория помощи'
        verbose_name_plural = 'Категории помощи'

    class MPTTMeta:
        order_insertion_by = ['name']


class HelpPage(models.Model):
    header = models.CharField(max_length=50,
                              verbose_name="Заголовок")
    content = models.TextField(verbose_name="Содержание")
    category = TreeForeignKey(CategoryHelp,
                              unique=True,
                              on_delete=models.PROTECT,
                              related_name="help",
                              verbose_name='Категория')

    def __str__(self):
        return self.header

    class Meta:
        verbose_name = "Помощь"
        verbose_name_plural = 'Помощь'
