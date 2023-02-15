# Generated by Django 4.1.1 on 2023-02-08 17:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drevo', '0048_subanswers'),
    ]

    operations = [
        migrations.AddField(
            model_name='interviewanswerexpertproposal',
            name='incorrect_answer_explanation',
            field=models.TextField(blank=True, verbose_name='Пояснение некорректности ответа'),
        ),
        migrations.AlterField(
            model_name='interviewanswerexpertproposal',
            name='is_incorrect_answer',
            field=models.BooleanField(default=False, verbose_name='Некорректный ответ'),
        ),
    ]