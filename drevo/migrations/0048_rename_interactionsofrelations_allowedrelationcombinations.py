# Generated by Django 3.2.4 on 2023-02-16 20:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('drevo', '0047_rename_initial_knowledge_type_interactionsofrelations_base_knowledge_type'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='InteractionsOfRelations',
            new_name='AllowedRelationCombinations',
        ),
    ]
