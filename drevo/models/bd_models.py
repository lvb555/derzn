from django.db import models




class TableState(models.Model):
    table_name = models.CharField(max_length=100)
    num_records = models.IntegerField()
    date_time = models.DateTimeField()
    difference = models.IntegerField(blank=True)



    class Meta:
        verbose_name = 'Состояние таблицы'
        verbose_name_plural = 'Состояния таблиц'

