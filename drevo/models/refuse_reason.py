from django.db import models


class RefuseReason(models.Model):
    reason = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Причина'
    )

    def __str__(self):
        return self.reason

    class Meta:
        verbose_name = 'Причина отказа'
        verbose_name_plural = 'Причины отказа'  