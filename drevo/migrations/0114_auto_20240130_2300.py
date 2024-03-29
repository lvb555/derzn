# Generated by Django 3.2.4 on 2024-01-30 20:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drevo', '0113_auto_20240124_0240'),
    ]

    operations = [
        migrations.AlterField(
            model_name='turple',
            name='is_global',
            field=models.IntegerField(choices=[(0, 'Локальный'), (1, 'Глобальный'), (2, 'Общий')], default=0, verbose_name='Глобальный'),
        ),
        migrations.AlterField(
            model_name='var',
            name='is_global',
            field=models.IntegerField(choices=[(0, 'Локальный'), (1, 'Глобальный'), (2, 'Общий')], default=0, verbose_name='Глобальная'),
        ),
    ]
