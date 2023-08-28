from django.shortcuts import render, get_object_or_404
from drevo.models import FriendsInviteTerm, Message
from drevo.models.feed_messages import FeedMessage
from users.models import User, MenuSections
from django.db.models.functions import Lower
from users.views import access_sections


def public_people_view(request):
    context = {'public_people': []}
    public_people = User.objects.filter(is_public=True).order_by(Lower('last_name').asc())
    context['public_people'] = public_people
    template_name = 'drevo/public_people.html'

    return render(request, template_name, context)

def public_human(request,id):
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
    template_name = 'drevo/public_human.html'
    return render(request, template_name, context)