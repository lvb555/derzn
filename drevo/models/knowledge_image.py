from django.db import models


class ZnImage(models.Model):
    znanie = models.ForeignKey('Znanie',
                               related_name='photos',
                               on_delete=models.PROTECT
                               )
    photo = models.ImageField(upload_to='photos/%Y/%m/%d/',
                              verbose_name='Фото',
                              blank=True
                              )

    def __str__(self):
        zn_name = str(self.znanie)[:40]
        return f'Фото № {self.id} для "{zn_name}"'
