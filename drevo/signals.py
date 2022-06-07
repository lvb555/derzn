import datetime

from django.core.mail import send_mail
from django.core.signals import request_finished
from django.db.models.signals import post_save
from django.dispatch import receiver

from dz import settings

from drevo.models import Znanie


def notify(sender, instance, created, **kwargs):
    print('in reciever')
    if not instance.is_published or not instance.author:
        return
    user_to_notify = instance.author.subscribers.all()
    if not user_to_notify:
        return
    message_subject = 'Новое знание'
    message_content = 'Уважаемый {}{}!\n' \
                      f'{datetime.date.today()} было создано новое' \
                      f'знание:\n  {instance.get_absolute_url()}\n' \
                      f'Автор: {instance.author}\n'
    for addressee in user_to_notify:
        patr = ''
        user_profile = addressee.profile
        if user_profile.first_name and user_profile.patronymic:
            patr = ' ' + user_profile.patronymic
        appeal = user_profile.first_name or 'пользователь'
        send_mail(message_subject, message_content.format(
        appeal, patr),
                    f'Дерево знаний <{settings.EMAIL_HOST_USER}>',
                    addressee.email)
