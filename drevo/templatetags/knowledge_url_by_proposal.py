from django.conf import settings
from django.template import Library
from django.urls import reverse

register = Library()


@register.filter(name='get_knowledge_url')
def knowledge_url_by_proposal(proposal_obj) -> str:
    """
        Фильтр для получения url на знание созданное на основе предложения эксперта
        :param proposal_obj:
        :return:
    """
    if proposal_obj.status == 'APPRVE':
        return f"{settings.BASE_URL}{reverse('zdetail', kwargs={'pk': proposal_obj.new_answer.pk})}"
    return f"{settings.BASE_URL}{reverse('zdetail', kwargs={'pk': proposal_obj.duplicate_answer.pk})}"
