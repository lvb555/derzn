from django.shortcuts import render, get_object_or_404
from users.models import User, MenuSections, Favourite
from users.views import access_sections
from ..relations_tree import get_knowledges_by_categories


def my_favourites(request,id):
    if request.method == 'GET':
        user = get_object_or_404(User, id=id)
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
            user_favourites = Favourite.objects.filter(user=user)
            user_favourites = user_favourites.first().favourites.filter(is_published=True)
            context['knowledges'] = user_favourites
            return render(request, 'drevo/my_favourites.html', context)