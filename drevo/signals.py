import datetime
import locale

from django.db.models.signals import post_save
from django.dispatch import receiver

from drevo.models import Znanie, Relation
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
    locale.setlocale(locale.LC_TIME, 'ru_RU')
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
    condition_elem = (not created, not instance.bz.is_published,
                      not instance.is_published, instance.bz.tz.name != 'Интервью')
    if any(condition_elem):
        return
    message_subj = 'Новое интервью'
    knowledge_url = settings.BASE_URL + instance.bz.get_absolute_url()
    date = instance.rz.name.split('-')
    message_text = 'Уважаемый {}{}!\n' \
                   f'Приглашаем Вас принять участие в новом интервью, которое состоится с ' \
                   f'{date[0]} по {date[1]}.\n' \
                   f'{knowledge_url} - интервью, \n' \
                   f'Администрация портала «Дерево знаний»'
    categories = instance.bz.get_ancestors_category()
    for category in categories:
        experts = category.get_experts()
        if not experts:
            continue
        for expert in experts:
            patronymic = ''
            user = expert.expert
            user_profile = user.profile
            if user.first_name and user_profile.patronymic:
                patronymic = ' ' + user_profile.patronymic
            name = user.first_name or 'Пользователь'
            send_email(user.email, message_subj, False, message_text.format(name, patronymic))
