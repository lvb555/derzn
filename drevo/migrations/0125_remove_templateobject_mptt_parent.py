# Generated by Django 3.2.4 on 2024-02-14 10:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('drevo', '0124_auto_20240211_1735'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='templateobject',
            name='mptt_parent',
        ),
    ]
