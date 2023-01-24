from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from drevo.models.label import Label

import json

from users.models import MenuSections, User


def sub_by_tag(request, id):
    if request.method == 'GET':
        labels = Label.objects.all()
        user = User.objects.get(id=id)
        if user == request.user:
            sections = [i.name for i in MenuSections.objects.all()]
            activity = [i.name for i in MenuSections.objects.all() if i.name.startswith('Мои') or
                        i.name.startswith('Моя')]
            link = 'users:myprofile'
        else:
            sections = [i.name for i in user.sections.all()]
            activity = [i.name for i in user.sections.all() if i.name.startswith('Мои') or i.name.startswith('Моя')]
            link = "'public_human' pub_user.id"
        return render(request, 'drevo/tag_subscription.html', {'labels': labels, 'pub_user': user, 'sections': sections,
                                                               'activity': activity, 'link': link})

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
