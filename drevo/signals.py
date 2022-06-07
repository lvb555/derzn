import datetime

from django.core.mail import send_mail
from dz import settings


def notify(sender, instance, created, **kwargs):
    if not instance.is_published or not instance.author:
        return
    user_to_notify = instance.author.subscribers.all()
    if not user_to_notify:
        return
    author_publication_url = settings.BASE_URL + instance.get_absolute_url()
    message_subject = 'Новое знание'
    message_content = 'Уважаемый {}{}!\n' \
                      f'{datetime.date.today()} было создано новое' \
                      f' знание:\n  {author_publication_url}\n' \
                      f'Автор: {instance.author}\n'
    for addressee in user_to_notify:
        patr = ''
        user_profile = addressee.profile
        if addressee.first_name and user_profile.patronymic:
            patr = ' ' + user_profile.patronymic
        appeal = addressee.first_name or 'пользователь'
        send_mail(message_subject, message_content.format(
            appeal, patr),
                  f'Дерево знаний <{settings.EMAIL_HOST_USER}>',
                  (addressee.email,))
