from django.db import models
from django.core.exceptions import ValidationError


class HelpPage(models.Model):
    """
    Метод save() Добавляет к имени тега '/', если его нет,
    или убирает если '/' добавлен в конец.
    """
    header = models.CharField(max_length=50,
                              verbose_name="Заголовок")
    content = models.TextField(verbose_name="Содержание")
    url_tag = models.CharField(max_length=20,
                               unique=True,
                               blank=True,
                               verbose_name="URL тег адреса",)

    def save(self, *args, **kwargs):
        if len(self.url_tag) == 0 or self.url_tag[0] != '/':
            self.url_tag = '/' + self.url_tag
        if len(self.url_tag) >= 2 and self.url_tag[-1] == '/':
            self.url_tag = self.url_tag[:-1]
        if HelpPage.objects.filter(url_tag=self.url_tag).exists():
            raise ValidationError("Значение поля url_tag должно быть уникальным")

        super().save(*args, **kwargs)

    def __str__(self):
        return self.header

    class Meta:
        verbose_name = "Помощь"
        verbose_name_plural = 'Помощь'
