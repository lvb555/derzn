from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect


import json

from drevo.models import Author
from users.models import MenuSections, User
from users.views import access_sections


def sub_by_author(request,id):
    if request.method == 'GET':
        user = User.objects.filter(id=id).first()
        context = {}
        if user is not None:
            context['authors'] = Author.objects.all()
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
            return render(request, 'drevo/author_subscription.html', context)


    if request.method == 'POST':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Данные с фронта {'Война в Донбассе': True, 'Грамматика': False}
            subscribed_to_authors = json.loads(request.body)
            authors_subscribed_to = Author.objects.filter(
                name__in=subscribed_to_authors)

            for author in authors_subscribed_to:
                if subscribed_to_authors[author.name]:
                    author.subscribers.add(request.user)
                elif not subscribed_to_authors[author.name]:
                    author.subscribers.remove(request.user)

        return redirect('subscribe_to_author',id=id)
