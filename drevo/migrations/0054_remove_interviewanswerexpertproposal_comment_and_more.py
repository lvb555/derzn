# Generated by Django 4.1.1 on 2023-02-17 23:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('drevo', '0053_merge_20230218_0123'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='interviewanswerexpertproposal',
            name='comment',
        ),
        migrations.AddField(
            model_name='subanswers',
            name='interview',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='inter_sub_answers', to='drevo.znanie', verbose_name='Интервью'),
        ),
    ]
