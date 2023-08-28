# Generated by Django 3.2.4 on 2023-07-14 09:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drevo', '0070_appeal'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appeal',
            name='subject',
            field=models.CharField(choices=[('question', 'Задать вопрос'), ('proposal', 'Сделать предложение по развитию сайта'), ('complaint', 'Заявить претензию')], max_length=200, verbose_name='Причина обращения'),
        ),
    ]
