# Generated by Django 3.2.4 on 2023-01-07 07:31

import colorfield.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('drevo', '0038_merge_20221226_2113'),
    ]

    operations = [
        migrations.AddField(
            model_name='knowledgegradescale',
            name='argument_color_background',
            field=colorfield.fields.ColorField(default='#00CC00', image_field=None, max_length=18, samples=None, verbose_name='Цвет фона довода "За"'),
        ),
        migrations.AddField(
            model_name='knowledgegradescale',
            name='argument_color_font',
            field=colorfield.fields.ColorField(default='#000000', image_field=None, max_length=18, samples=None, verbose_name='Цвет шрифта довода "За"'),
        ),
        migrations.AddField(
            model_name='knowledgegradescale',
            name='contraargument_color_background',
            field=colorfield.fields.ColorField(default='#FD0B33', image_field=None, max_length=18, samples=None, verbose_name='Цвет фона довода "Против"'),
        ),
        migrations.AddField(
            model_name='knowledgegradescale',
            name='contraargument_color_font',
            field=colorfield.fields.ColorField(default='#000000', image_field=None, max_length=18, samples=None, verbose_name='Цвет шрифта довода "Против"'),
        ),
    ]
