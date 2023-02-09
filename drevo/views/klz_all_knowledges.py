from django.shortcuts import render
from loguru import logger
from users.models import MenuSections
from ..models import Znanie, KnowledgeStatuses
from ..relations_tree import get_knowledges_by_categories
from drevo.common import variables
from django.db.models import Q


logger.add('logs/main.log',
           format="{time} {level} {message}", rotation='100Kb', level="ERROR")


def klz_all(request):
    context = {}
    context['sections'] = [i.name for i in MenuSections.objects.all()]
    context['activity'] = [i.name for i in MenuSections.objects.all() if i.name.startswith('Мои') or
                           i.name.startswith('Моя')]
    context['link'] = 'users:myprofile'
    context['pub_user'] = request.user
    #Берем все знания со статусами "Предзнание в КЛЗ" и "Знание в КЛЗ"
    knowledges = KnowledgeStatuses.objects.filter(Q(status='PRE_KLZ') | Q(status='KLZ'))
    context['categories'], context['knowledges'] = \
        get_knowledges_by_categories([i.knowledge for i in knowledges])
    context['znanie_tree'] = context['categories'].get_ancestors(include_self=True)
    context['var'] = variables
    return render(request, 'drevo/klz_all.html', context)