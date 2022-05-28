# Generated by Django 3.2.4 on 2022-05-28 14:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('drevo', '0012_auto_20220426_1733'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='category',
            managers=[
            ],
        ),
        migrations.CreateModel(
            name='BrowsingHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(auto_now_add=True, verbose_name='Дата просмотра')),
                ('user', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
                ('znanie', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.PROTECT, to='drevo.znanie', verbose_name='Знание')),
            ],
            options={
                'verbose_name': 'Просмотр',
                'verbose_name_plural': 'Просмотры',
                'ordering': ('-date',),
            },
        ),
    ]
