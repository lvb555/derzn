import datetime

from django.conf import settings
from django.db import models
from django.utils.timezone import now

from .knowledge import Znanie


class InterviewResultsSendingSchedule(models.Model):
    """
        Модель в которой хранится информация о рассылках результатов интервью (рассписание)
    """
    interview = models.OneToOneField(
        verbose_name='Интервью',
        to=Znanie,
        on_delete=models.CASCADE,
        related_name='sending_schedule',
        help_text='Выберите знание, вид которого "Интервью"'
    )
    next_sending = models.DateTimeField(
        verbose_name='Дата возможной рассылки',
        auto_now_add=True
    )
    last_sending = models.DateTimeField(
        verbose_name='Дата последней рассылки',
        auto_now=True
    )

    class Meta:
        verbose_name = 'Рассылка результатов интервью'
        verbose_name_plural = 'Рассылки результатов интервью'
        ordering = ['-next_sending']

    def save(self, *args, **kwargs):
        # Проверка на то, что знание это интервью
        if (not self.pk) and (self.interview.tz.name != 'Интервью'):
            raise ValueError('В поле interview должно храниться знание, вид которого "Интервью"')
        # Если запись уже была создана, то увеличиваем время следующей рассылки на NOT_MORE_OFTEN дней
        if self.pk:
            self.next_sending = now() + datetime.timedelta(days=settings.NOT_MORE_OFTEN)
        return super(InterviewResultsSendingSchedule, self).save(*args, **kwargs)

    def __str__(self):
        return f'Sending for: {self.interview}'
