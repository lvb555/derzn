from django.db import models

class Turple(models.Model):
    """
        объект Справочник в сервисе созданя документов
    """

    knowledge = models.ForeignKey(
        to='drevo.Znanie', 
        on_delete=models.CASCADE, 
        verbose_name="Знание")

    name = models.CharField(max_length=255, verbose_name="Название")
    is_global = models.BooleanField(verbose_name="Глобальный", default=False)
    weight = models.IntegerField(default=100, verbose_name="Порядок")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Словарь'
        verbose_name_plural = 'Словари'
