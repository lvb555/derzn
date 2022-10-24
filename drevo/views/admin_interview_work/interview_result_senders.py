from django.conf import settings
from django.db.models import F, Q
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from ...models import Relation, Tr
from ...sender import send_email


def get_base_message_context(proposal_obj) -> dict:
    interview_url = f"{settings.BASE_URL}{reverse_lazy('zdetail', kwargs={'pk': proposal_obj.interview.pk})}"
    context = dict(
        expert=proposal_obj.expert,
        interview_name=proposal_obj.interview.name,
        question_name=proposal_obj.question.name,
        expert_proposal=proposal_obj.new_answer_text,
        is_agreed=proposal_obj.is_agreed,
        interview_url=interview_url
    )
    return context


def send_accept_proposal(proposal_obj) -> None:
    """
        Функция для рассылки уведомлений экспертам чьи предложения были одобрены
    """
    context = get_base_message_context(proposal_obj)

    new_answer = proposal_obj.new_answer
    email_address = context.get('expert').email
    if context.get('is_agreed'):
        message_subject = 'Изменение Вашего ответа'
    else:
        message_subject = 'Ваше предложение принято!'
    new_answer_url = f"{settings.BASE_URL}{reverse_lazy('zdetail', kwargs={'pk': new_answer.pk})}"
    context.update({'new_answer': new_answer, 'new_answer_url': new_answer_url})
    message_html = render_to_string('email_templates/interview_result_email/interview_accept_email.html', context)
    send_email(email_address, message_subject, message_html, message_html)


def send_not_accept_proposal(proposal_obj) -> None:
    """
        Функция для рассылки уведомлений экспертам чьи предложения не были одобрены
    """
    context = get_base_message_context(proposal_obj)

    email_address = context.get('expert').email
    message_subject = 'Ваше предложение не принято!'
    context.update({'admin_comment': proposal_obj.admin_comment})
    message_html = render_to_string('email_templates/interview_result_email/interview_not_accept_email.html', context)
    send_email(email_address, message_subject, message_html, message_html)


def send_duplicate_answer_proposal(proposal_obj) -> None:
    """
        Функция для рассылки уведомлений экспертам чьи предложения дублируют ответ
    """
    context = get_base_message_context(proposal_obj)

    existing_answer = proposal_obj.answer
    email_address = context.get('expert').email
    if context.get('is_agreed'):
        message_subject = 'Изменение Вашего ответа'
    else:
        message_subject = 'Ваше предложение не принято!'
    existing_answer_url = f"{settings.BASE_URL}{reverse_lazy('zdetail', kwargs={'pk': existing_answer.pk})}"
    context.update({'existing_answer': existing_answer, 'existing_answer_url': existing_answer_url})
    message_html = render_to_string('email_templates/interview_result_email/interview_duplicate_answer_email.html',
                                    context)
    send_email(email_address, message_subject, message_html, message_html)


def send_duplicate_proposal(proposal_obj) -> None:
    """
        Функция для рассылки уведомлений экспертам чьи предложения дублируют предложение
    """
    context = get_base_message_context(proposal_obj)
    existing_answer = proposal_obj.answer
    email_address = context.get('expert').email
    if context.get('is_agreed'):
        message_subject = 'Изменение Вашего ответа'
    else:
        message_subject = 'Ваше предложение не принято!'
    existing_answer_url = f"{settings.BASE_URL}{reverse_lazy('zdetail', kwargs={'pk': existing_answer.pk})}"
    context.update({'existing_answer': existing_answer, 'existing_answer_url': existing_answer_url})
    message_html = render_to_string('email_templates/interview_result_email/interview_duplicate_proposal_email.html',
                                    context)
    send_email(email_address, message_subject, message_html, message_html)


def send_new_answers(interview_name, question_name, proposals) -> None:
    """
        Функция для рассылки уведомлений экспертам о появлении новых ответов на интервью
    """
    experts = proposals.values(
        first_name=F('expert__first_name'), last_name=F('expert__last_name'), email=F('expert__email')
    ).order_by().distinct()
    new_answers = proposals.filter(status='APPRVE').values_list('new_answer__name', flat=True)
    tr_obj = Tr.objects.get(name='Ответ [ы]')
    answers = Relation.objects.select_related('bz', 'rz').filter(
        Q(bz__name=question_name) & Q(tr=tr_obj)
    ).values_list('rz__name', flat=True)

    context = dict(
        interview_name=interview_name,
        question_name=question_name,
        answers=answers,
        new_answers=new_answers
    )

    for expert in experts:
        email_address = expert.get('email')
        message_subject = 'Новые ответы!'
        context['expert'] = expert
        message_html = render_to_string('email_templates/interview_result_email/interview_new_answer_email.html',
                                        context)
        send_email(email_address, message_subject, message_html, message_html)
