from django.shortcuts import render, redirect

from drevo.models.label import Label

import json


def sub_by_tag(request):
    if request.method == 'GET':
        labels = Label.objects.all()
        return render(request, 'drevo/tag_subscription.html', {'labels': labels})

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

        return redirect('subscription_by_tag')
