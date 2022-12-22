from django.conf import settings
from django.template import Library
from django.urls import reverse

from ..models import Znanie

register = Library()


@register.filter(name='get_knowledge_url')
def knowledge_url_by_proposal(proposal_obj) -> str:
    """
        Фильтр для получения url на знание созданное на основе предложения эксперта
        :param proposal_obj:
        :return:
    """
    try:
        if proposal_obj.status == 'APPRVE':
            return f"{settings.BASE_URL}{reverse('zdetail', kwargs={'pk': proposal_obj.new_answer.pk})}"
        return f"{settings.BASE_URL}{reverse('zdetail', kwargs={'pk': proposal_obj.duplicate_answer.pk})}"
    except Exception:
        return ''


@register.inclusion_tag('email_templates/interview_result_email/expert_results_accepted.html')
def get_interview_results_accepted(proposals, proposals_un_notified):
    return dict(proposals=proposals, proposals_un_notified=proposals_un_notified)


@register.inclusion_tag('email_templates/interview_result_email/expert_results_duplicates.html')
def get_interview_results_duplicates(proposals, proposals_un_notified):
    return dict(proposals=proposals, proposals_un_notified=proposals_un_notified)


@register.inclusion_tag('email_templates/interview_result_email/expert_results_not_accepted.html')
def get_interview_results_not_accepted(proposals, proposals_un_notified):
    return dict(proposals=proposals, proposals_un_notified=proposals_un_notified)


@register.inclusion_tag('email_templates/interview_result_email/expert_results_unprocessed.html')
def get_interview_results_unprocessed(interview, question, proposals):
    question_pk = Znanie.objects.filter(name=question).first().pk
    interview_url_kwargs = {'interview_pk': interview.pk, 'question_pk': question_pk}
    interview_url = f"{settings.BASE_URL}{reverse('question_expert_work', kwargs=interview_url_kwargs)}"
    return dict(proposals=proposals, interview_url=interview_url, interview_name=interview.name)
