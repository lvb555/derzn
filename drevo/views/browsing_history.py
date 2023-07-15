from django.shortcuts import render
from loguru import logger
from users.models import User, MenuSections
from users.views import access_sections
from ..models import BrowsingHistory, Comment, FriendsInviteTerm, Message
from ..models.feed_messages import FeedMessage

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
            invite_count = FriendsInviteTerm.objects.filter(recipient=request.user.id).count()
            context['invite_count'] = invite_count if invite_count else 0
            context['new_knowledge_feed'] = FeedMessage.objects.filter(recipient=user, was_read=False).count()
            context['new_messages'] = Message.objects.filter(recipient=user, was_read=False).count()
            context['new'] = int(context['new_knowledge_feed']) + int(
                context['invite_count'] + int(context['new_messages']))
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