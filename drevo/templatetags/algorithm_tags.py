from django.template import Library
from django.utils.safestring import mark_safe
from drevo.models import Znanie, Relation, QuestionToKnowledge, AlgorithmAdditionalElements
from drevo.templatetags.constructors_tag import is_max_number_of_inner_rels_for_zn

register = Library()


@register.simple_tag
def recurse_dict(data, previous_knowledge, algorithm, user=None, work=None, html='', display='block',
                 complicated_knowledge=None, mode=None, constructor=None):
    if constructor and algorithm == previous_knowledge:
        html += f'<span class="algorithm-element ms-2"><a href="{algorithm.get_absolute_url()}">{algorithm.name}</a></span>'
        html = constructor_mode_add_function(algorithm, html)
        html = constructor_mode_redaction_functions(html, edit_function='editMainZnanie()', delete_function=f'deleteMainZnanie(`algorithm`, { algorithm.id })')
        if data:
            html += f'<i class="ms-2 bi bi-play-circle-open" onclick="toggleHiddenElement(this);"></i>'
    html += f'<ul style="display: {display}">'
    # Создание html с необходимой вложенностью
    for child in data:
        if isinstance(child, Znanie) or (isinstance(child, dict) and not list(child.values())[0]):
            if isinstance(child, dict):
                child = list(child.keys())[0]
            rel, parent = find_relation(child, complicated_knowledge, previous_knowledge)
            rel_name = ','.join(list(rel.values_list('tr__name', flat=True)))
            html += f'<li value="{rel_name}">'
            element_type = child.tz.name
            if element_type != 'Комментарий':
                html += f'<span class="text-secondary d-flex align-items-center">{rel_name}'
                if constructor:
                    html = constructor_mode_redaction_functions(html, edit_function=f'edit_relation({rel.first().id})', delete_function=f'delete_relation({ parent.id }, { child.pk })')
                html += f'</span>'
                if algorithm.several_works is False:
                    work = 'Данные по алгоритму'
                if user.is_authenticated and work:
                    if AlgorithmAdditionalElements.objects.filter(user=user, work__work_name=work,
                                                                                     algorithm=algorithm,
                                                                                     parent_element=child,
                                                                                     insertion_type=0).exists():
                        element_type = 'Блок'
                html += f'<input disabled type="checkbox" class="simple-elements" value="{element_type}" onclick="nextAction(this)">'\
                        f'<span class="algorithm-element ms-2"><a href="{child.get_absolute_url()}">{child.name}</a> ' \
                        f'({element_type}){find_extra_span(child)}</span>'
                if mode and rel_name != 'Вариант' and not (element_type != 'Блок' and rel_name in ['Можно сделать', 'Нужно сделать']):
                    html += f'<i class="bi bi-plus-lg text-success p-2" onclick="addNewElement(this);"></i>'
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
                    html = add_user_elements(additional_elements, html, mode)
            if constructor:
                html = constructor_mode_add_function(child, html)
            previous_knowledge = child
        elif isinstance(child, dict):
            rel, parent = find_relation(list(child.keys())[0], complicated_knowledge, previous_knowledge)
            rel_name = ','.join(list(rel.values_list('tr__name', flat=True)))
            html += f'<li value="{rel_name}">'
            if list(child.keys())[0].tz.name != 'Комментарий':
                html += f'<span class="text-secondary d-flex align-items-center">{rel_name}'
                if constructor:
                    html = constructor_mode_redaction_functions(html, edit_function=f'edit_relation({rel.first().id})',
                                                                delete_function=f'delete_relation({parent.id}, {list(child.keys())[0].pk})')
                html += f'</span>'\
                        f'<input disabled type="checkbox" class="simple-elements" value="{list(child.keys())[0].tz}" onclick="nextAction(this)">'\
                        f'<span class="algorithm-element ms-2"><a href="{list(child.keys())[0].get_absolute_url()}">' \
                        f'{list(child.keys())[0]}</a> ({list(child.keys())[0].tz}){find_extra_span(list(child.keys())[0])}</span>'
                if mode:
                    if rel_name != 'Вариант' and not (list(child.keys())[0].tz.name != 'Блок' and rel_name in ['Можно сделать', 'Нужно сделать']):
                        html += f'<i class="bi bi-plus-lg text-success py-2 ps-2" onclick="addNewElement(this);"></i>'
                    html += f'<i class="bi bi-play-circle-close mx-2" onclick="toggleHiddenElement(this);"></i>'
            else:
                html += f'<span style="display: none;">{list(child.keys())[0].name} ({list(child.keys())[0].tz})</span>'
            if QuestionToKnowledge.objects.filter(knowledge=list(child.keys())[0], publication=True).count() > 0:
                html += f'<a class="btn question" href="{list(child.keys())[0].get_absolute_url()}/questions_user"><i class="bi bi-question-lg"></i></a>'
            if constructor:
                html = constructor_mode_add_function(list(child.keys())[0], html)
                html += f'<i class="ms-1 bi bi-play-circle-open" onclick="toggleHiddenElement(this);"></i>'
            if list(child.values())[0]:
                html = recurse_dict(list(child.values())[0], list(child.keys())[0], algorithm, user=user, work=work,
                                    html=html, display='block' if constructor else 'none', complicated_knowledge=list(child.keys())[0], mode=mode, constructor=constructor)
            html += f'</li>'
            if algorithm.several_works is False:
                work = 'Данные по алгоритму'
            if user.is_authenticated and work:
                additional_elements = AlgorithmAdditionalElements.objects.filter(user=user, work__work_name=work, algorithm=algorithm,
                                                                                 parent_element=list(child.keys())[0]).order_by('insertion_type')
                if additional_elements:
                    html = add_user_elements(additional_elements, html, mode)
            previous_knowledge = list(child.keys())[0]
    html += f'</ul>'
    return mark_safe(html)


def find_relation(elem, complicated_knowledge, previous_knowledge):
    rel = Relation.objects.filter(bz=complicated_knowledge, rz=elem)
    parent = complicated_knowledge
    if not rel:
        rel = Relation.objects.filter(bz=previous_knowledge, rz=elem)
        parent = previous_knowledge
    return rel, parent


def find_extra_span(elem):
    extra_span = ''
    if elem.files.exists() or (elem.content is not None and elem.content != ""):
        extra_span += f'<span class="tooltip-text">'
        if elem.content is not None and elem.content != "":
            extra_span += f'По этому знанию есть дополнительная информация.'
        if elem.files.count() > 1:
            extra_span += f'У этого знания есть прикрепленные файлы.'
        elif elem.files.count() == 1:
            extra_span += f'У этого знания есть прикрепленный файл.'
        extra_span += f'</span>'
    return mark_safe(extra_span)

def add_user_elements(queryset, html, mode):
    flag = False
    if queryset.filter(insertion_type=0):
        html = html[:-10]
        flag = True
    for new_elem in queryset:
        common_part = f'<input disabled type="checkbox" class="simple-elements" value="Действие" onclick="nextAction(this)">' \
                      f'<span class="algorithm-element ms-2"><a class="new-element">{new_elem.element_name}</a> (Действие)</span>'
        if mode:
            if new_elem.insertion_type == 1:
                common_part += f'''<i class="bi bi-plus-lg text-success p-2" onclick="addNewElement(this);"></i>'''
            common_part += f'''<i class="bi bi-pencil-fill text-warning p-2" onclick="redactOrDelete(this, 'same', 'redact');"></i>''' \
                           f'''<i class="bi bi-x-lg text-danger p-2" onclick="redactOrDelete(this, 'same', 'delete');"></i>'''
        else:
            common_part += f'</li>'
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


def constructor_mode_redaction_functions(html, edit_function=None, delete_function=None):
    html += f'<i class="text-info mt-1 me-2 ms-2 align-top" onclick="{edit_function}" style="cursor: pointer;">'\
                    f'<svg xmlns="http://www.w3.org/2000/svg" width="25" height="25" fill="currentColor" class="bi bi-pen" viewBox="0 0 16 16">'\
                        f'<path d="m13.498.795.149-.149a1.207 1.207 0 1 1 1.707 1.708l-.149.148a1.5 1.5 0 0 1-.059 2.059L4.854 14.854a.5.5 0 0 1-.233.131l-4 1a.5.5 0 0 1-.606-.606l1-4a.5.5 0 0 1 .131-.232l9.642-9.642a.5.5 0 0 0-.642.056L6.854 4.854a.5.5 0 1 1-.708-.708L9.44.854A1.5 1.5 0 0 1 11.5.796a1.5 1.5 0 0 1 1.998-.001zm-.644.766a.5.5 0 0 0-.707 0L1.95 11.756l-.764 3.057 3.057-.764L14.44 3.854a.5.5 0 0 0 0-.708l-1.585-1.585z"/>'\
                    f'</svg>'\
            f'</i>'\
            f'<i class="text-danger mt-1 me-2 align-top" onclick="{delete_function}" style="cursor: pointer;">'\
                f'<svg xmlns="http://www.w3.org/2000/svg" width="25" height="25" fill="currentColor" class="bi bi-x-lg" viewBox="0 0 16 16">'\
                    f'<path d="M2.146 2.854a.5.5 0 1 1 .708-.708L8 7.293l5.146-5.147a.5.5 0 0 1 .708.708L8.707 8l5.147 5.146a.5.5 0 0 1-.708.708L8 8.707l-5.146 5.147a.5.5 0 0 1-.708-.708L7.293 8 2.146 2.854Z"/>'\
                f'</svg>'\
            f'</i>'

    return mark_safe(html)


def constructor_mode_add_function(elem, html):
    if not is_max_number_of_inner_rels_for_zn(elem):
        html += f'<i class="text-success mt-1 me-2 ms-2 align-top" id="add_knowledge" onclick="add_relation({ elem.pk })" style="cursor: pointer;">'\
                    f'<svg xmlns="http://www.w3.org/2000/svg" width="25" height="25" fill="currentColor" class="bi bi-plus-lg" viewBox="0 0 16 16">'\
                        f'<path fill-rule="evenodd" d="M8 2a.5.5 0 0 1 .5.5v5h5a.5.5 0 0 1 0 1h-5v5a.5.5 0 0 1-1 0v-5h-5a.5.5 0 0 1 0-1h5v-5A.5.5 0 0 1 8 2Z"></path>'\
                    f'</svg>'\
                f'</i>'
    return mark_safe(html)