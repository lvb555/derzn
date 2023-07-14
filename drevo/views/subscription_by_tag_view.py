from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from drevo.models import FriendsInviteTerm, Message
from drevo.models.feed_messages import FeedMessage
from drevo.models.label import Label

import json

from users.models import MenuSections, User
from users.views import access_sections


def sub_by_tag(request, id):
    if request.method == 'GET':
        user = User.objects.filter(id=id).first()
        context = {}
        if user is not None:
            context['labels'] = Label.objects.all()
            if user == request.user:
                context['sections'] = access_sections(user)
                context['activity'] = [i for i in context['sections'] if i.startswith('Мои') or
                                       i.startswith('Моя')]
                context['link'] = 'users:myprofile'
                invite_count = len(FriendsInviteTerm.objects.filter(recipient=user.id))
                context['invite_count'] = invite_count if invite_count else 0
                context['new_knowledge_feed'] = FeedMessage.objects.filter(recipient=user, was_read=False).count()
                context['new_messages'] = Message.objects.filter(recipient=user, was_read=False).count()
                context['new'] = int(context['new_knowledge_feed']) + int(
                    context['invite_count'] + int(context['new_messages']))
            else:
                context['sections'] = [i.name for i in user.sections.all()]
                context['activity'] = [i.name for i in user.sections.all() if i.name.startswith('Мои') or i.name.startswith('Моя')]
                context['link'] = 'public_human'
                context['id'] = id
            context['pub_user'] = user
            return render(request, 'drevo/tag_subscription.html', context)

    if request.method == 'POST':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Данные с фронта {'Война в Донбассе': True, 'Грамматика': False}
            subscribed_to_tags = json.loads(request.body)
            tags_subscribed_to = Label.objects.filter(
                name__in=subscribed_to_tags)

            for tag in tags_subscribed_to:
                if subscribed_to_tags[tag.name]:
                    tag.subscribers.add(request.user)
                elif not subscribed_to_tags[tag.name]:
                    tag.subscribers.remove(request.user)

        return redirect('subscription_by_tag',id=id)
