from django.db import models


class HelpPage(models.Model):
    header = models.CharField(max_length=50, verbose_name="Заголовок")
    content = models.TextField(verbose_name="Содержание")
    url_tag = models.CharField(max_length=20, unique=True, blank=True, verbose_name="URL тег адреса")

    def save(self, *args, **kwargs):
        self.url_tag = '/' + self.url_tag
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Помощь"
        verbose_name_plural = 'Помощь'
