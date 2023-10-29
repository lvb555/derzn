from django.template import Library
from django.utils.safestring import mark_safe
from drevo.models import Znanie, Relation, QuestionToKnowledge

register = Library()


@register.simple_tag
def recurse_dict(data, previous_knowledge, html='', display='block', complicated_knowledge=None):
    html += f'<ul style="display: {display}">'
    # Создание html с необходимой вложенностью
    for child in data:
        if isinstance(child, Znanie):
            rel = ','.join(list(Relation.objects.filter(bz=complicated_knowledge, rz=child).values_list('tr__name', flat=True)))
            if not rel:
                rel = ','.join(list(
                    Relation.objects.filter(bz=previous_knowledge, rz=child).values_list('tr__name', flat=True)))
            html += f'<li value="{rel}">'
            if child.tz.name != 'Комментарий':
                html += f'<span class="text-secondary d-flex">{rel}</span>'
            if child.tz.name != 'Комментарий':
                html += f'<input disabled type="checkbox" class="simple-elements" value="{child.tz}" onclick="nextAction(this)">'
                extra_span = ''
                if child.files.exists() or (child.content is not None and child.content != ""):
                    extra_span += f'<span class="tooltip-text">'
                    if child.content is not None and child.content != "":
                        extra_span += f'По этому знанию есть дополнительная информация.'
                    if child.files.count() > 1:
                        extra_span += f'У этого знания есть прикрепленные файлы.'
                    elif child.files.count() == 1:
                        extra_span += f'У этого знания есть прикрепленный файл.'
                    extra_span += f'</span>'
                html += f'<span class="algorithm-element"><a href="{child.get_absolute_url()}">{child.name}</a> ' \
                        f'({child.tz}){extra_span}</span>'
            else:
                html += f'<span style="display: none;">{child.name} ({child.tz})</span>'
            if QuestionToKnowledge.objects.filter(knowledge=child, publication=True).count() > 0:
                html += f'<a class="btn question" href="{child.get_absolute_url()}/questions_user"><i class="bi bi-question-lg"></i></a>'
            html += f'</li>'
            previous_knowledge = child
        elif isinstance(child, dict):
            rel = ','.join(list(Relation.objects.filter(bz=complicated_knowledge, rz=list(child.keys())[0]).values_list('tr__name', flat=True)))
            if not rel:
                rel = ','.join(list(Relation.objects.filter(bz=previous_knowledge, rz=list(child.keys())[0]).values_list('tr__name',
                                                                                                         flat=True)))
            html += f'<li value="{rel}">'
            if list(child.keys())[0].tz.name != 'Комментарий':
                html += f'<span class="text-secondary d-flex">{rel}</span>'
            if list(child.keys())[0].tz.name != 'Комментарий':
                html += f'<input disabled type="checkbox" class="simple-elements" value="{list(child.keys())[0].tz}" onclick="nextAction(this)">'
                extra_span = ''
                if list(child.keys())[0].files.exists() or (list(child.keys())[0].content is not None and list(child.keys())[0].content != ""):
                    extra_span += f'<span class="tooltip-text">'
                    if list(child.keys())[0].content is not None and list(child.keys())[0].content != "":
                        extra_span += f'По этому знанию есть дополнительная информация.'
                    if list(child.keys())[0].files.count() > 1:
                        extra_span += f'У этого знания есть прикрепленные файлы.'
                    elif list(child.keys())[0].files.count() == 1:
                        extra_span += f'У этого знания есть прикрепленный файл.'
                    extra_span += f'</span>'
                html += f'<span class="algorithm-element"><a href="{list(child.keys())[0].get_absolute_url()}">' \
                        f'{list(child.keys())[0]}</a>({list(child.keys())[0].tz}){extra_span}</span>'
            else:
                html += f'<span style="display: none;">{list(child.keys())[0].name} ({list(child.keys())[0].tz})</span>'
            if list(child.values())[0]:
                html = recurse_dict(list(child.values())[0], list(child.keys())[0], html=html, display='none', complicated_knowledge=list(child.keys())[0])
            if QuestionToKnowledge.objects.filter(knowledge=list(child.keys())[0], publication=True).count() > 0:
                html += f'<a class="btn question" href="{list(child.keys())[0].get_absolute_url()}/questions_user"><i class="bi bi-question-lg"></i></a>'
            html += f'</li>'
            previous_knowledge = list(child.keys())[0]
    html += f'</ul>'
    return mark_safe(html)
