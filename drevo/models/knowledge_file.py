from django.db import models

from drevo.common.file_storage import ASCIIFileSystemStorage


class ZnFile(models.Model):
    znanie = models.ForeignKey(
        'Znanie',
        related_name='files',
        on_delete=models.CASCADE
    )
    file = models.FileField(
        upload_to='files/%Y/%m/%d/',
        verbose_name='Файл',
        blank=True,
        storage=ASCIIFileSystemStorage()
    )
    objects = models.Manager()

    def __str__(self):
        zn_name = str(self.znanie)[:40]
        return f'Файл № {self.id} для "{zn_name}"'
