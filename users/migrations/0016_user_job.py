# Generated by Django 3.2.4 on 2023-01-19 16:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0015_auto_20230118_1833'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='job',
            field=models.CharField(blank=True, max_length=150, verbose_name='Работа'),
        ),
    ]
