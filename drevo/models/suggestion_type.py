from django.db import models


class SuggestionKind(models.Model):
    type_name = models.CharField(max_length=255, verbose_name='Название типа')
    weight = models.IntegerField(verbose_name='Порядок', default=100, blank=True)

    def __str__(self):
        return self.type_name

    class Meta:
        verbose_name = 'Вид предложения'
        verbose_name_plural = 'Виды предложений'