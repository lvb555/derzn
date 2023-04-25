from tabnanny import verbose
from django.db import models
from users.models import User
from drevo.models import Znanie
from .label_feed_message import LabelFeedMessage

from datetime import datetime


class FeedMessage(models.Model):
    """
    Таблица для хранения сообщений ленты
    """
    sender = models.ForeignKey(User, verbose_name='Отправитель', related_name='message_sender',
                               on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, verbose_name='Получатель', related_name='message_recipient',
                                  on_delete=models.CASCADE)
    label = models.ForeignKey(LabelFeedMessage, verbose_name='Ярлык сообщения', on_delete=models.CASCADE)
    znanie = models.ForeignKey(Znanie, verbose_name='Знание', related_name='message_znanie',
                               on_delete=models.CASCADE)
    text = models.TextField(max_length=511, verbose_name='Текст сообщения')
    date_time = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время отправки')
    was_read = models.BooleanField(default=False, verbose_name='Прочитано')

    class Meta:
        verbose_name = 'Сообщение ленты'
        verbose_name_plural = 'Сообщения ленты'

    def __str__(self) -> str:
        return str(self.sender) + " -> " + str(self.recipient) + ": " + str(self.znanie.name)

    def get_time(self) -> str:
        message_date = self.date_time.date()
        today_date = datetime.today().date()

        try:
            diff = int(str(today_date - message_date).split()[0])

            if diff < 30:
                return f'{diff} дн. назад'

            elif diff >= 30 and diff <= 365:
                months = diff // 30
                return f'{months} мес. назад'
            else:
                years = diff // 365
                return f'{years} г. назад'
        except ValueError:
            return 'сегодня'
