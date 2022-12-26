from django.db import models

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

    def is_interview(self):
        # Проверка на то, что знание это интервью
        if self.interview.tz.name != 'Интервью':
            raise ValueError('В поле interview должно храниться знание, вид которого "Интервью"')

    def __str__(self):
        return f'Sending for: {self.interview}'
