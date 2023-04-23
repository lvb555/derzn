from django.db import models
from users.models import User

from datetime import datetime


class Message(models.Model):
    """
    Таблица Сообщения
    """
    sender = models.ForeignKey(User, verbose_name='Отправитель', related_name='sender_of_message',
                               on_delete=models.DO_NOTHING)
    recipient = models.ForeignKey(User, verbose_name='Получатель', related_name='recipient_of_message',
                                  on_delete=models.DO_NOTHING)
    text = models.TextField(max_length=511, verbose_name='Текст сообщения')
    date_time = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время отправки')
    was_read = models.BooleanField(default=False, verbose_name='Прочитано')

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'

    def __str__(self) -> str:
        return str(self.sender) + " -> " + str(self.recipient)

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
