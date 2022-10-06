from django.db import models

from .validators import validate_tag


class HelpPage(models.Model):
    header = models.CharField(max_length=50, verbose_name="Заголовок")
    content = models.TextField(verbose_name="Содержание")
    tag = models.CharField(max_length=20,
                           unique=True,
                           validators=[validate_tag],
                           verbose_name="URL тег адреса")

    class Meta:
        verbose_name = "Помощь"
        verbose_name_plural = 'Помощь'
