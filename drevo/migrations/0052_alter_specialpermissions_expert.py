# Generated by Django 4.1.1 on 2023-02-15 21:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('drevo', '0051_merge_20230216_0033'),
    ]

    operations = [
        migrations.AlterField(
            model_name='specialpermissions',
            name='expert',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='expert', to=settings.AUTH_USER_MODEL, verbose_name='Эксперт'),
        ),
    ]
