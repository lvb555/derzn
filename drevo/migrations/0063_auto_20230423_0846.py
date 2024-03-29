# Generated by Django 3.2.4 on 2023-04-23 05:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('drevo', '0062_alter_relationshiptztr_base_tz_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='browsinghistory',
            name='znanie',
            field=models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, to='drevo.znanie', verbose_name='Знание'),
        ),
        migrations.AlterField(
            model_name='feedmessage',
            name='label',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='drevo.labelfeedmessage', verbose_name='Ярлык сообщения'),
        ),
        migrations.AlterField(
            model_name='feedmessage',
            name='recipient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='message_recipient', to=settings.AUTH_USER_MODEL, verbose_name='Получатель'),
        ),
        migrations.AlterField(
            model_name='feedmessage',
            name='sender',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='message_sender', to=settings.AUTH_USER_MODEL, verbose_name='Отправитель'),
        ),
        migrations.AlterField(
            model_name='feedmessage',
            name='znanie',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='message_znanie', to='drevo.znanie', verbose_name='Знание'),
        ),
        migrations.AlterField(
            model_name='znimage',
            name='znanie',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='photos', to='drevo.znanie'),
        ),
    ]
