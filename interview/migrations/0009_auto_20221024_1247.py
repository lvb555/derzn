# Generated by Django 3.2.4 on 2022-10-24 08:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('interview', '0008_auto_20221023_1425'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='interviewquestion',
            options={'verbose_name': 'Вопросы интервью', 'verbose_name_plural': 'Вопросы интервью'},
        ),
        migrations.RemoveField(
            model_name='interviewquestion',
            name='c_question',
        ),
    ]
