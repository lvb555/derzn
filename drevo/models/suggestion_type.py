from django.db import models


class SuggestionType(models.Model):
    type_name = models.CharField(max_length=255, verbose_name='Название типа')
    weight = models.IntegerField(verbose_name='Вес для сортировки', primary_key=True)

    def __str__(self):
        return self.type_name

    class Meta:
        verbose_name = 'Вид предложения'
        verbose_name_plural = 'Виды предложений'
