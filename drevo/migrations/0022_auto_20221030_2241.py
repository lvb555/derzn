# Generated by Django 3.2.4 on 2022-10-30 19:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drevo', '0021_auto_20221030_2231'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ageusersscale',
            options={'ordering': ('min_age',), 'verbose_name': 'Границы возраста', 'verbose_name_plural': 'Шкала возраста пользователей'},
        ),
        migrations.AlterField(
            model_name='ageusersscale',
            name='max_age',
            field=models.PositiveSmallIntegerField(blank=True, verbose_name='Правая граница возраста'),
        ),
        migrations.AlterField(
            model_name='ageusersscale',
            name='min_age',
            field=models.PositiveSmallIntegerField(blank=True, verbose_name='Левая граница возраста'),
        ),
    ]
