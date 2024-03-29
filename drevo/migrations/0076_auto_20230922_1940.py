# Generated by Django 3.2.4 on 2023-09-22 16:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drevo', '0075_questiontoknowledge_useranswertoquestion'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='questiontoknowledge',
            options={'verbose_name': 'Вопрос', 'verbose_name_plural': 'Вопросы пользователям'},
        ),
        migrations.AlterModelOptions(
            name='useranswertoquestion',
            options={'verbose_name': 'Ответ на вопрос', 'verbose_name_plural': 'Ответы на вопросы'},
        ),
        migrations.AlterField(
            model_name='questiontoknowledge',
            name='question',
            field=models.CharField(max_length=255, verbose_name='Вопрос'),
        ),
    ]
