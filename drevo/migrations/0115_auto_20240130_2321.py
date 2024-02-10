# Generated by Django 3.2.4 on 2024-01-30 20:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drevo', '0114_auto_20240130_2300'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='turple',
            name='is_global',
        ),
        migrations.RemoveField(
            model_name='var',
            name='is_global',
        ),
        migrations.AddField(
            model_name='turple',
            name='availability',
            field=models.IntegerField(choices=[(0, 'Локальный'), (1, 'Глобальный'), (2, 'Общий')], default=0, verbose_name='Доступность'),
        ),
        migrations.AddField(
            model_name='var',
            name='availability',
            field=models.IntegerField(choices=[(0, 'Локальный'), (1, 'Глобальный'), (2, 'Общий')], default=0, verbose_name='Доступность'),
        ),
    ]
