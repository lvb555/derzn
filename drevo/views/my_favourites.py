from django.shortcuts import render, get_object_or_404
from users.models import User, MenuSections, Favourite
from users.views import access_sections
from ..models import FriendsInviteTerm, Message
from ..models.feed_messages import FeedMessage


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
                invite_count = len(FriendsInviteTerm.objects.filter(recipient=user.id))
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
            user_favourites = Favourite.objects.filter(user=user)
            user_favourites = user_favourites.first().favourites.filter(is_published=True)
            context['knowledges'] = user_favourites
            return render(request, 'drevo/my_favourites.html', context)