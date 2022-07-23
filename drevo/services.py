from django.conf import settings
from django.template.loader import render_to_string

from drevo.models import Znanie
from drevo.sender import send_email


def send_notify_interview(interview, date):
    """
    Осуществляет формирование сообщения для отправки уведомления экспертам об интервью.
    Для отправки сообщения используется функция send_email
    :param interview: экземпляр модели Знание с видом Интервью
    :param date: список - период проведения интервью [дата начала, дата окончания]
    :return: None
    """

    # Получаем список вопросов к интервью
    question_set = Znanie.objects.filter(is_published=True, related__bz__id=interview.id,
                                         related__tr__name='Состав', related__is_published=True)
    # Если вопросы в интервью отсутствуют, завершаем работу
    if not question_set:
        return False

    message_subj = 'Новое интервью'
    knowledge_url = settings.BASE_URL + f'/drevo/interview/{interview.id}/'
    question_base_url = settings.BASE_URL + '/drevo/znanie/'
    context = {
        'start_date': date[0],
        'end_date': date[1],
        'url': knowledge_url,
        'question_set': question_set,
        'question_base_url': question_base_url,
        'interview_name': interview.name
    }

    categories = interview.get_ancestors_category()
    send_result = True
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
            context['name'] = name
            context['patronymic'] = patronymic
            message_text = render_to_string('interview_notify_email.txt', context)
            message_html = render_to_string('interview_notify_email.html', context)
            result = send_email(user.email, message_subj, message_html, message_text)
            if not result:
                send_result = False
    return send_result
