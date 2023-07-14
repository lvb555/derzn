from django.shortcuts import render, redirect
import json
from drevo.models import Category, FriendsInviteTerm, Message
from drevo.models.feed_messages import FeedMessage
from users.models import MenuSections, User
from users.views import access_sections


def sub_by_category(request, id):
    if request.method == 'GET':
        user = User.objects.filter(id=id).first()
        context = {}
        if user is not None:
            context['categories'] = [i.name for i in Category.objects.filter(subscribers=user,is_published=True)]
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
            categories = Category.tree_objects.exclude(is_published=False)
            block_list = Category.tree_objects.exclude(is_published=True)
            block_child = []
            for item in block_list:
                block_child += [i.pk for i in item.get_descendants(include_self=False)]
            categories = categories.exclude(pk__in=block_child)
            context['ztypes'] = categories
            return render(request, 'drevo/category_subscription.html', context)

    if request.method == 'POST':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Данные с фронта {'Война в Донбассе': True, 'Грамматика': False}
            subscribed_to_category = json.loads(request.body)
            category_subscribed_to = Category.objects.filter(
                name__in=subscribed_to_category)

            for category in category_subscribed_to:
                if subscribed_to_category[category.name]:
                    category.subscribers.add(request.user)
                elif not subscribed_to_category[category.name]:
                    category.subscribers.remove(request.user)

        return redirect('subscription_by_category',id=id)
