# Generated by Django 3.2.4 on 2024-02-08 10:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drevo', '0121_auto_20240208_1355'),
    ]

    operations = [
        migrations.AlterField(
            model_name='turple',
            name='weight',
            field=models.IntegerField(default=1, verbose_name='Порядок'),
        ),
        migrations.AlterField(
            model_name='turpleelement',
            name='weight',
            field=models.IntegerField(default=1, verbose_name='Порядок'),
        ),
        migrations.AlterField(
            model_name='var',
            name='structure',
            field=models.IntegerField(choices=[(0, 'Переменная'), (1, 'Массив'), (2, 'Управление')], default=0, verbose_name='Тип объекта'),
        ),
        migrations.AlterField(
            model_name='var',
            name='weight',
            field=models.IntegerField(default=1, verbose_name='Порядок'),
        ),
    ]