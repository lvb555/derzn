# Generated by Django 3.2.4 on 2023-09-19 15:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('drevo', '0074_merge_20230917_1610'),
        ('users', '0025_suggestiontype'),
    ]

    operations = [
        migrations.AddField(
            model_name='usersuggection',
            name='suggestions_type',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='users.suggestiontype', verbose_name='Вид предложения'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='usersuggection',
            name='parent_knowlege',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.DO_NOTHING, to='drevo.znanie', verbose_name='Родительское знание'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='usersuggection',
            name='user',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='suggestions', to='users.user', verbose_name='Пользователь, предложивший знание'),
            preserve_default=False,
        ),
    ]
