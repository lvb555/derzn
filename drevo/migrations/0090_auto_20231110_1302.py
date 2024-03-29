# Generated by Django 3.2.4 on 2023-11-10 10:02

from django.db import migrations, models
import drevo.common.file_storage


class Migration(migrations.Migration):

    dependencies = [
        ('drevo', '0089_merge_0088_auto_20231102_1827_0088_auto_20231107_2208'),
    ]

    operations = [
        migrations.AlterField(
            model_name='author',
            name='photo',
            field=models.ImageField(blank=True, null=True, storage=drevo.common.file_storage.ASCIIFileSystemStorage(), upload_to='photos/authors/', verbose_name='Фото'),
        ),
        migrations.AlterField(
            model_name='developer',
            name='photo',
            field=models.ImageField(blank=True, null=True, storage=drevo.common.file_storage.ASCIIFileSystemStorage(), upload_to='photos/developers/', verbose_name='Фото'),
        ),
        migrations.AlterField(
            model_name='znfile',
            name='file',
            field=models.FileField(blank=True, storage=drevo.common.file_storage.ASCIIFileSystemStorage(), upload_to='files/%Y/%m/%d/', verbose_name='Файл'),
        ),
        migrations.AlterField(
            model_name='znimage',
            name='photo',
            field=models.ImageField(blank=True, storage=drevo.common.file_storage.ASCIIFileSystemStorage(), upload_to='photos/%Y/%m/%d/', verbose_name='Фото'),
        ),
    ]
