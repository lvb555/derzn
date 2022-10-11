from django.template import Library

register = Library()


@register.filter(name='translate_status_expert_proposal')
def translate_status_expert_proposal(status_value):
    status_dict = dict(APPRVE="Принят", REJECT="Не принят", ANSDPL="Дублирует ответ", RESDPL="Дублирует предложение")
    return status_dict.get(status_value)
