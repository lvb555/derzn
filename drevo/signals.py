import datetime
import locale

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.urls import reverse

from drevo.models import Znanie, Relation
from drevo.services import send_notify_interview
from dz import settings

from drevo.sender import send_email
from loguru import logger

logger.add('logs/main.log',
           format="{time} {level} {message}", rotation='100Kb', level="INFO")


def notify(sender, instance: Znanie, created, **kwargs):
    """Sends messages with application to author subscribers on knowledge creation"""
    if not all((instance.is_published, instance.author, created,
                not instance.tz.is_systemic)):
        return
    user_to_notify = instance.author.subscribers.all()
    if not user_to_notify:
        return
    author_publication_url = settings.BASE_URL + instance.get_absolute_url()
    message_subject = 'Новое знание'
    months = {
        1: "января",
        2: "февраля",
        3: "марта",
        4: "апреля",
        5: "мая",
        6: "июня",
        7: "июля",
        8: "августа",
        9: "сентября",
        10: "октября",
        11: "ноятбря",
        12: "декабря",
    }
    date_now = datetime.date.today()
    cur_month_formed = months[date_now.month]
    date_with_month = date_now.strftime(f'%d {cur_month_formed} %Y')
    message_content = 'Уважаемый {}{}!\n' \
                      f'{date_with_month} было создано новое' \
                      f' знание:\n  {author_publication_url}\n' \
                      f'Автор: {instance.author}\n'
    for addressee in user_to_notify:
        patr = ''
        user_profile = addressee.profile
        if addressee.first_name and user_profile.patronymic:
            patr = ' ' + user_profile.patronymic
        appeal = addressee.first_name or 'пользователь'
        send_email(addressee.email, message_subject, False,
                   message_content.format(appeal, patr))


@receiver(post_save, sender=Relation)
def notify_new_interview(sender, instance, created, **kwargs):
    """
    Сигнал, который создает рассылку экспертам с коментенциями соответствующей категории и ее предков о
    публикации знания вида "Интервью"
    """
    # Настраиваем сигнал для срабатывания при создании связи вида "Период интервью"
    # Условия для проверки публикации связи, интервью и периода интервью
    condition_publish = (instance.is_published, instance.bz.is_published, instance.rz.is_published)

    # Условия для проверки, что вид связи соответствует "Период интервью" и базовое знание "Интервью"
    condition_name = (instance.bz.tz.name == 'Интервью', instance.tr.name == 'Период интервью')

    # Проверяем первоначальные условия и, если им не соответствуем, завершаем работу сигнала
    if not all((*condition_publish, *condition_name, created)):
        return

    # Получаем период интервью
    date = instance.rz.name.split('-')

    # Передаем параметры в функцию send_notify_interview, которая формирует текст сообщения
    send_notify_interview(instance.bz, date)
