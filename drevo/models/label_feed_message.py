from django.db import models


class LabelFeedMessage(models.Model):
    """
    Таблица для хранения ярлыков сообщений ленты
    """
    name = models.CharField(max_length=31, verbose_name='Название')


    class Meta:
        verbose_name = 'Ярлык сообщений ленты'
        verbose_name_plural = 'Ярлыки сообщений ленты'


    def __str__(self) -> str:
        return self.name