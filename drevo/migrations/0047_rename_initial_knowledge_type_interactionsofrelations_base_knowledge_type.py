# Generated by Django 3.2.4 on 2023-02-03 20:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('drevo', '0046_alter_interactionsofrelations_options'),
    ]

    operations = [
        migrations.RenameField(
            model_name='interactionsofrelations',
            old_name='initial_knowledge_type',
            new_name='base_knowledge_type',
        ),
    ]
