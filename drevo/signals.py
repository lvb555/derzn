import datetime
import locale

from drevo.models import Znanie
from dz import settings

from drevo.sender import send_email
from loguru import logger

logger.add('logs/main.log',
           format="{time} {level} {message}", rotation='100Kb', level="INFO")


def notify(sender, instance: Znanie, created, **kwargs):
    if not instance.is_published or not instance.author or instance.tz.is_systemic:
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
