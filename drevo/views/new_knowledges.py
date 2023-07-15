from django.shortcuts import render, get_object_or_404
from drevo.models import Category, Label, Author, FriendsInviteTerm, Message
from drevo.models.feed_messages import FeedMessage
from users.models import User, MenuSections
from users.views import access_sections


def new_knowledge(request, id):
    user = get_object_or_404(User, id=id)
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
        category_sub = Category.objects.filter(subscribers=user, is_published=True)
        tag_sub = Label.objects.filter(subscribers=user)
        author_sub = [i.id for i in Author.objects.filter(subscribers=user)]
        main_knowledges = user.knowledge_to_notification_page.all()
        context['knowledges_by_authors'] = main_knowledges.filter(author__in=author_sub)
        context['knowledges_by_labels'] = main_knowledges.filter(labels__in=tag_sub)
        context['knowledges_by_categories'] = main_knowledges.filter(category__in=category_sub)
        return render(request, 'drevo/new_knowledge.html', context)
