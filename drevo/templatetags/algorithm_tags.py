from django.template import Library
from django.utils.safestring import mark_safe
from drevo.models import Znanie, Relation

register = Library()


@register.simple_tag
def recurse_dict(data, previous_knowledge, html='', display='block', complicated_knowledge=None):
    html += f'<ul style="display: {display}">'
    # Создание html с необходимой вложенностью
    for child in data:
        if isinstance(child, Znanie):
            rel = ','.join(list(Relation.objects.filter(bz=previous_knowledge, rz=child).values_list('tr__name', flat=True)))
            if not rel:
                rel = ','.join(list(
                    Relation.objects.filter(bz=complicated_knowledge, rz=child).values_list('tr__name', flat=True)))
            html += f'<li value="{rel}">'\
                    f'<span class="text-secondary d-flex">{rel}</span>'
            if rel in ['Вариант', 'Состав блока']:
                html += f'<input disabled type="checkbox" class="start" onclick="startAction(this)">'
            if child.tz.name != 'Комментарий':
                html += f'<input disabled type="checkbox" class="simple-elements" value="{child.tz}" onclick="nextAction(this)">'
            html += f'<span>{child.name} ({child.tz})</span>' \
                    f'</li>'
            previous_knowledge = child
        elif isinstance(child, dict):
            rel = ','.join(list(Relation.objects.filter(bz=previous_knowledge, rz=list(child.keys())[0]).values_list('tr__name', flat=True)))
            if not rel:
                rel = ','.join(list(
                    Relation.objects.filter(bz=complicated_knowledge, rz=list(child.keys())[0]).values_list('tr__name',
                                                                                                         flat=True)))
            html += f'<li value="{rel}">' \
                    f'<span class="text-secondary d-flex">{rel}</span>'
            if rel in ['Вариант', 'Состав блока']:
                html += f'<input disabled type="checkbox" class="start" onclick="startAction(this)">'
            if list(child.keys())[0].tz.name != 'Комментарий':
                html += f'<input disabled type="checkbox" class="simple-elements" value="{list(child.keys())[0].tz}" onclick="nextAction(this)">'
            html += f'<span>{list(child.keys())[0]} ({list(child.keys())[0].tz})</span>'
            html = recurse_dict(list(child.values())[0], list(child.keys())[0], html=html, display='none', complicated_knowledge=list(child.keys())[0])
            html += f'</li>'
            previous_knowledge = list(child.keys())[0]
    html += f'</ul>'
    return mark_safe(html)
