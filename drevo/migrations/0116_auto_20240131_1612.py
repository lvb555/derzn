# Generated by Django 3.2.4 on 2024-01-31 13:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('drevo', '0115_auto_20240130_2321'),
    ]

    operations = [
        migrations.AlterField(
            model_name='var',
            name='availability',
            field=models.IntegerField(choices=[(0, 'Локальный'), (1, 'Глобальный'), (2, 'Общий')], default=0, verbose_name='Класс объекта'),
        ),
        migrations.AlterField(
            model_name='var',
            name='connected_to',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='drevo.var', verbose_name='Родитель'),
        ),
        migrations.AlterField(
            model_name='var',
            name='is_main',
            field=models.BooleanField(default=False, verbose_name='Группа'),
        ),
        migrations.AlterField(
            model_name='var',
            name='structure',
            field=models.IntegerField(choices=[(0, 'Переменная'), (1, 'Массив'), (2, 'Справочник'), (3, 'Итератор'), (4, 'Условие')], default=0, verbose_name='Тип объекта'),
        ),
        migrations.AlterField(
            model_name='var',
            name='type_of',
            field=models.IntegerField(choices=[(0, 'Текст'), (1, 'Число'), (2, 'Дата')], default=0, verbose_name='Вид значения'),
        ),
    ]
