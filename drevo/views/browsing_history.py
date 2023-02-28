from django.shortcuts import render
from loguru import logger
from django.http import HttpResponseRedirect
from django.urls import reverse
from users.models import User, MenuSections
from users.views import access_sections
from ..models import BrowsingHistory, Comment

logger.add('logs/main.log',
    format="{time} {level} {message}", rotation='100Kb', level="ERROR")


def browsing_history(request, id):
    user = User.objects.filter(id=id).first()
    context = {}
    if user is not None:
        if user == request.user:
            context['sections'] = access_sections(user)
            context['activity'] = [i for i in context['sections'] if i.startswith('Мои') or
                                   i.startswith('Моя')]
            context['link'] = 'users:myprofile'
        else:
            context['sections'] = [i.name for i in user.sections.all()]
            context['activity'] = [i.name for i in user.sections.all() if
                                   i.name.startswith('Мои') or i.name.startswith('Моя')]
            context['link'] = 'public_human'
            context['id'] = id

        context['pub_user'] = user
        browsing_history_by_user = BrowsingHistory.objects.filter(user=user).order_by('-date')
        history = []

        # получаем комментарии
        for item in browsing_history_by_user:
            if item.znanie.is_published:
                obj = {}
                obj["znanie"] = item.znanie
                history.append(obj)

        context['history'] = history
        return render(request, "drevo/browsing_history.html", context)