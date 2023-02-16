import datetime
import locale

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.urls import reverse

from drevo.models import Znanie, Relation
from drevo.services import send_notify_interview
from dz import settings
from django.db import transaction

from drevo.sender import send_email
from loguru import logger

logger.add(
    "logs/main.log", format="{time} {level} {message}", rotation="100Kb", level="INFO"
)


# Функция notify, которая передается в on_commit(), будет вызвана сразу после того, как гипотетическая запись в базу данных, сделанная там,
# где on_commit() вызывается, будет успешно зафиксирована.
# Обработчик работает с инстансом Znanie, у которого уже добавлены теги.
def on_transaction_commit(func):
    def inner(*args, **kwargs):
        transaction.on_commit(lambda: func(*args, **kwargs))

    return inner


@on_transaction_commit
def notify(sender, instance: Znanie, created, **kwargs):
    if sender._meta.object_name == "Migrate":
        breakpoint()
        return
    """Sends messages with application to author subscribers on knowledge creation"""
    tz_model = instance.__class__.tz.field.remote_field.model

    if (
        not instance.is_published
        or not instance.author
        or not created
        or not tz_model.objects.filter(id=instance.tz_id).exists()
        or instance.tz.is_systemic
    ):
        return

    user_to_notify = set(instance.author.subscribers.all())

    for knowledge_tags in instance.labels.all():
        # Объеденяем множества. Так у нас не будут повторяться пользовотели, которым нужно отправить уведомление.
        user_to_notify = user_to_notify | set(knowledge_tags.subscribers.all())

    # Проверяем, есть ли категория и добавляем пользователей, подписанных на нее или ее parent
    if instance.category:
        knowledge_categories = instance.category.get_ancestors(include_self=True)
        for knowledge_category in knowledge_categories:
            user_to_notify = user_to_notify | set(knowledge_category.subscribers.all())

    if not user_to_notify:
        return
    author_publication_url = settings.BASE_URL + instance.get_absolute_url()
    message_subject = "Новое знание"
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
        11: "ноября",
        12: "декабря",
    }
    date_now = datetime.date.today()
    cur_month_formed = months[date_now.month]

    date_with_month = date_now.strftime(f'%d {cur_month_formed} %Y')

    context = {
        'date_with_month': date_with_month,
        'author_publication_url': author_publication_url,
        'instance_name': instance.name,
        'instance_author': instance.author
    }


    for addressee in user_to_notify:
        patr = ""
        user_profile = addressee.profile
        if addressee.first_name and user_profile.patronymic:

            patr = ' ' + user_profile.patronymic
        appeal = addressee.first_name or 'пользователь'

        context['appeal'] = appeal
        context['patr'] = patr

        message_text = render_to_string('email_templates/subscribe_notify_email.txt', context)
        message_html = render_to_string('email_templates/subscribe_notify_email.html', context)

        send_email(addressee.email, message_subject, message_html, message_text)


@receiver(post_save, sender=Relation)
def notify_new_interview(sender, instance, created, **kwargs):
    """
    Сигнал, который создает рассылку экспертам с коментенциями соответствующей категории и ее предков о
    публикации знания вида "Интервью"
    """
    # Настраиваем сигнал для срабатывания при создании связи вида "Период интервью"
    # Условия для проверки публикации связи, интервью и периода интервью
    condition_publish = (
        instance.is_published,
        instance.bz.is_published,
        instance.rz.is_published,
    )

    # Условия для проверки, что вид связи соответствует "Период интервью" и базовое знание "Интервью"
    condition_name = (
        instance.bz.tz.name == "Интервью",
        instance.tr.name == "Период интервью",
    )

    # Проверяем первоначальные условия и, если им не соответствуем, завершаем работу сигнала
    if not all((*condition_publish, *condition_name, created)):
        return

    # Получаем период интервью
    date = instance.rz.name

    # Передаем параметры в функцию send_notify_interview, которая формирует текст сообщения
    send_notify_interview(instance.bz, date)
