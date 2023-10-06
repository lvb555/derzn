from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('users', '0030_auto_20231006_0933'),
    ]

    operations = [
        migrations.AddField(
            model_name='usersuggection',
            name='knowledge_type_id',
            field=models.IntegerField(),
            preserve_default=False,
        ),
    ]