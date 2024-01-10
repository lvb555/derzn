from django.db import models

class TurpleElement(models.Model):
    """
        объект Элемент справочника в сервисе создания документов
    """

    value = models.CharField(max_length=255, verbose_name="Содержание")
    turple = models.ForeignKey(
        to='drevo.Turple', 
        on_delete=models.CASCADE, 
        verbose_name="Справочник")
    weight = models.IntegerField(default=100, verbose_name="Порядок")
    var = models.ForeignKey(
        to='drevo.Var',
        on_delete=models.CASCADE,
        null=True,
        verbose_name='Переменная')

    class Meta:
        verbose_name = 'Элемент словаря'
        verbose_name_plural = 'Элементы словаря'