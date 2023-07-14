from django.shortcuts import render
from loguru import logger
from users.models import User, MenuSections
from users.views import access_sections
from ..models import Znanie, SpecialPermissions, FriendsInviteTerm, Message
from ..models.feed_messages import FeedMessage
from ..relations_tree import get_knowledges_by_categories
from drevo.common import variables


logger.add('logs/main.log',
           format="{time} {level} {message}", rotation='100Kb', level="ERROR")


def my_knowledge(request, id):
    if request.method == 'GET':
        user = User.objects.filter(id=id).first()
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
            context['expert_categories'] = SpecialPermissions.objects.filter(expert__id=id).values_list('categories__name')
            knowledges_of_author = Znanie.published.filter(
                author__user_author__id=id)
            context['categories'], context['knowledges'] = \
                get_knowledges_by_categories(knowledges_of_author)
            context['znanie_tree'] = context['categories'].filter(name__in=context['expert_categories'])\
                .get_ancestors(include_self=True)
            context['var'] = variables
            context['title'] = 'Мои знания'
            context['under_title'] = 'Мой вклад, как эксперта'
            return render(request, 'drevo/my_knowledge.html', context)


def my_preknowledge(request, id):
    if request.method == 'GET':
        user = User.objects.filter(id=id).first()
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
            context['expert_categories'] = SpecialPermissions.objects.filter(expert__id=id).values_list('categories__name')
            knowledges_of_author = Znanie.published.filter(
                author__user_author__id=id)
            context['categories'], context['knowledges'] = \
                get_knowledges_by_categories(knowledges_of_author)
            context['znanie_tree'] = context['categories'].exclude(name__in=context['expert_categories'])\
                .get_ancestors(include_self=True)
            context['var'] = variables
            context['title'] = 'Мои знания'
            context['under_title'] = 'Мой вклад, как пользователя'
            return render(request, 'drevo/my_knowledge.html', context)


def my_expertise(request, id):
    if request.method == 'GET':
        user = User.objects.filter(id=id).first()
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
            knowledges_of_expert = Znanie.published.filter(
                expert__id=id)
            context['categories'], context['knowledges'] = \
                get_knowledges_by_categories(knowledges_of_expert)
            context['znanie_tree'] = context['categories'].get_ancestors(include_self=True)
            context['var'] = variables
            context['title'] = 'Мои экспертизы'
            context['under_title'] = 'Мой вклад, как эксперта'
            return render(request, 'drevo/my_knowledge.html', context)
