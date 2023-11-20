from django.template import Library
from django.utils.safestring import mark_safe
from drevo.models import Znanie, Relation, QuestionToKnowledge, AlgorithmAdditionalElements

register = Library()


@register.simple_tag
def recurse_dict(data, previous_knowledge, algorithm, user=None, work=None, html='', display='block',
                 complicated_knowledge=None, mode=None):
    html += f'<ul style="display: {display}">'
    # Создание html с необходимой вложенностью
    for child in data:
        if isinstance(child, Znanie) or (isinstance(child, dict) and not list(child.values())[0]):
            if isinstance(child, dict):
                child = list(child.keys())[0]
            rel = ','.join(list(Relation.objects.filter(bz=complicated_knowledge, rz=child).values_list('tr__name', flat=True)))
            if not rel:
                rel = ','.join(list(
                    Relation.objects.filter(bz=previous_knowledge, rz=child).values_list('tr__name', flat=True)))
            html += f'<li value="{rel}">'
            element_type = child.tz.name
            if element_type != 'Комментарий':
                html += f'<span class="text-secondary d-flex">{rel}</span>'
            if element_type != 'Комментарий':
                if algorithm.several_works is False:
                    work = 'Данные по алгоритму'
                if user.is_authenticated and work:
                    if AlgorithmAdditionalElements.objects.filter(user=user, work__work_name=work,
                                                                                     algorithm=algorithm,
                                                                                     parent_element=child,
                                                                                     insertion_type=0).exists():
                        element_type = 'Блок'
                html += f'<input disabled type="checkbox" class="simple-elements" value="{element_type}" onclick="nextAction(this)">'
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
                html += f'<span class="algorithm-element ms-2"><a href="{child.get_absolute_url()}">{child.name}</a> ' \
                        f'({element_type}){extra_span}</span>'
                if mode and rel not in ['Вариант', 'Можно сделать', 'Нужно сделать']:
                    html += f'<button onclick="addNewElement(this);"><i class="bi bi-pencil-fill"></i></button>'
            else:
                html += f'<span style="display: none;">{child.name} ({element_type})</span>'
            if QuestionToKnowledge.objects.filter(knowledge=child, publication=True).count() > 0:
                html += f'<a class="btn question" href="{child.get_absolute_url()}/questions_user"><i class="bi bi-question-lg"></i></a>'
            if element_type == 'Блок':
                html += f'<ul></ul>'
            html += f'</li>'
            if user.is_authenticated and work:
                additional_elements = AlgorithmAdditionalElements.objects.filter(user=user, work__work_name=work, algorithm=algorithm,
                                                                                 parent_element=child).order_by('insertion_type')
                if additional_elements:
                    html = add_user_elements(additional_elements, html)
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
                html += f'<span class="algorithm-element ms-2"><a href="{list(child.keys())[0].get_absolute_url()}">' \
                        f'{list(child.keys())[0]}</a> ({list(child.keys())[0].tz}){extra_span}</span>'
                if mode and rel not in ['Вариант', 'Можно сделать', 'Нужно сделать']:
                    html += f'<button onclick="addNewElement(this);"><i class="bi bi-pencil-fill"></i></button>'
            else:
                html += f'<span style="display: none;">{list(child.keys())[0].name} ({list(child.keys())[0].tz})</span>'
            if QuestionToKnowledge.objects.filter(knowledge=list(child.keys())[0], publication=True).count() > 0:
                html += f'<a class="btn question" href="{list(child.keys())[0].get_absolute_url()}/questions_user"><i class="bi bi-question-lg"></i></a>'
            if list(child.values())[0]:
                html = recurse_dict(list(child.values())[0], list(child.keys())[0], algorithm, user=user, work=work,
                                    html=html, display='none', complicated_knowledge=list(child.keys())[0], mode=mode)
            html += f'</li>'
            if algorithm.several_works is False:
                work = 'Данные по алгоритму'
            if user.is_authenticated and work:
                additional_elements = AlgorithmAdditionalElements.objects.filter(user=user, work__work_name=work, algorithm=algorithm,
                                                                                 parent_element=list(child.keys())[0]).order_by('insertion_type')
                if additional_elements:
                    html = add_user_elements(additional_elements, html)
            previous_knowledge = list(child.keys())[0]
    html += f'</ul>'
    return mark_safe(html)


def add_user_elements(queryset, html):
    flag = False
    if queryset.filter(insertion_type=0):
        html = html[:-10]
        flag = True
    for new_elem in queryset:
        common_part = f'<input disabled type="checkbox" class="simple-elements" value="Действие" onclick="nextAction(this)">' \
                      f'<span class="algorithm-element ms-2"><a class="new-element">{new_elem.element_name}</a> (Действие)</span></li>'
        if new_elem.insertion_type == 0:
            rel = 'Можно сделать'
            if new_elem.relation_type == 'necessary':
                rel = 'Нужно сделать'
            html += f'<li value="{rel}"><span class="text-secondary d-flex">{rel}</span>{common_part}'
        else:
            if flag:
                flag = False
                html += f'</ul></li>'
            html += f'<li value="Далее"><span class="text-secondary d-flex">Далее</span>{common_part}'
    if flag:
        html += f'</ul>'
    html += f'</li>'
    return mark_safe(html)
