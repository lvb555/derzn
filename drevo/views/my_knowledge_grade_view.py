from drevo.models import FriendsInviteTerm, Message
from drevo.models.feed_messages import FeedMessage
from drevo.models.knowledge import Znanie
from drevo.models.knowledge_grade import KnowledgeGrade
from drevo.models.category import Category
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from users.models import User, MenuSections
import copy

from users.views import access_sections


def my_knowledge_grade(request, id) -> HttpResponse:
    """
    Страница "Мои оценки знания"
    """
    if request.method == 'GET':
        context = {}
        user = User.objects.filter(id=id).first()
        if user is not None:
            if user == request.user:
                context['sections'] = access_sections(user)
                context['activity'] = [i for i in context['sections'] if i.startswith('Мои') or
                                       i.startswith('Моя')]
                context['link'] = 'users:myprofile'
                invite_count = len(FriendsInviteTerm.objects.filter(recipient=request.user.id))
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

        tmp_request = copy.copy(request)
        request.user = user
        context['false_request'] = request

        knowledges_grade = KnowledgeGrade.objects.prefetch_related("knowledge")\
                                                 .exclude(knowledge__category=None)\
                                                 .filter(user=user)
        knowledges_dict = {}
        category_names = []
        for knowledge_grade in knowledges_grade:
            category = knowledge_grade.knowledge.category
            if category is not None:
                if not category.name in knowledges_dict:
                    knowledges_dict[category.name] = []
                knowledges_dict[category.name].append(knowledge_grade.knowledge)
                category_names.append(category.name)
                while category.parent:
                    category = category.parent
                    category_names.append(category)

        context['zn_dict'] = knowledges_dict
        context['ztypes'] = Category.tree_objects.exclude(is_published=False)\
                                          .filter(name__in=category_names)
        request = copy.copy(tmp_request)

        return render(request, "drevo/my_knowledge_grade.html", context)
