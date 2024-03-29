# Generated by Django 3.2.4 on 2023-11-20 04:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drevo', '0090_auto_20231110_1302'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='glossaryterm',
            options={'ordering': ('order',), 'verbose_name': 'Термин глоссария', 'verbose_name_plural': 'Термины глоссария'},
        ),
        migrations.RemoveField(
            model_name='relationshiptztr',
            name='is_only_one_rel',
        ),
        migrations.RemoveField(
            model_name='tz',
            name='tr',
        ),
        migrations.AddField(
            model_name='tz',
            name='max_number_of_inner_rels',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='Максимальное число внутренних связей'),
        ),
        migrations.AddField(
            model_name='tz',
            name='min_number_of_inner_rels',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='Минимальное число внутренних связей'),
        ),
    ]
