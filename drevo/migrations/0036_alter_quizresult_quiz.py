# Generated by Django 3.2.4 on 2022-12-24 08:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('drevo', '0035_auto_20221223_1251'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quizresult',
            name='quiz',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='passed_quizzes', to='drevo.znanie', verbose_name='Тест'),
        ),
    ]
