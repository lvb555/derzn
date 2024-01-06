from django.db import models

from drevo.common.file_storage import ASCIIFileSystemStorage


class ZnImage(models.Model):
    znanie = models.ForeignKey(
        'Znanie',
        related_name='photos',
        on_delete=models.CASCADE
    )
    photo = models.ImageField(
        upload_to='photos/%Y/%m/%d/',
        verbose_name='Фото',
        blank=True,
        storage=ASCIIFileSystemStorage()
    )
    objects = models.Manager()

    def __str__(self):
        zn_name = str(self.znanie)[:40]
        return f'Фото № {self.id} для "{zn_name}"'
