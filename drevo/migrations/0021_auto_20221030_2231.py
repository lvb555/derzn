# Generated by Django 3.2.4 on 2022-10-30 19:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('drevo', '0020_friendsinviteterm'),
    ]

    operations = [
        migrations.CreateModel(
            name='AgeUsersScale',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('min_age', models.PositiveSmallIntegerField(verbose_name='Левая граница возраста')),
                ('max_age', models.PositiveSmallIntegerField(verbose_name='Правая граница возраста')),
            ],
        ),
        migrations.AlterField(
            model_name='friendsterm',
            name='friend',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='friends', to=settings.AUTH_USER_MODEL, verbose_name='Друг'),
        ),
        migrations.AlterField(
            model_name='friendsterm',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='users', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
    ]