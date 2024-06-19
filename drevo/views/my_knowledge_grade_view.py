from drevo.models import FriendsInviteTerm, Message, Relation
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


def search_category(knowledge: Znanie) -> Category | None:
    """ Ищем категорию знания среди ближайших предков
        Классический bfs
        ищем всех предков, находим их категории.
        Если у предка нет категории, то ищем у их предков и т.д.
    """

    queue = [knowledge]
    visited = set()
    visited.add(knowledge)

    while queue:
        knowledge = queue.pop(0)
        if knowledge.category:
            return knowledge.category
        for parent in Relation.objects.filter(tr__is_argument=True, rz=knowledge).select_related('bz',
                                                                                                 'bz__category').all():
            if parent.bz.category:
                return parent.bz.category
            elif parent.bz not in visited:
                visited.add(parent.bz)
                queue.append(parent.bz)

    return None


def my_knowledge_grade(request, id) -> HttpResponse:
    """
    Страница "Мои оценки знания"
    """
    if request.method == 'GET':
        context = {}
        user = User.objects.filter(id=id).first()
        if not user:
            return HttpResponse('Пользователь id:{id} не найден')

        # далее заполняется контекст для показа в шапке профиля
        if user == request.user:
            # секции меню для показа в шапке профиля
            context['sections'] = access_sections(user)
            # Меню активность
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
        knowledges_grade = (KnowledgeGrade.objects
                            .prefetch_related("knowledge", "knowledge__category")
                            .filter(user=user))

        knowledges_dict = {}
        categories = []

        for knowledge_grade in knowledges_grade:
            category = knowledge_grade.knowledge.category
            if not category:
                category = search_category(knowledge_grade.knowledge)

            if category not in knowledges_dict:
                knowledges_dict[category] = []
            knowledges_dict[category].append({'knowledge': knowledge_grade.knowledge, 'grade': knowledge_grade.grade})

            # добавляем все родительские категории до самого верха
            while category:
                categories.append(category)
                category = category.parent

        context['zn_dict'] = knowledges_dict
        context['ztypes'] = Category.tree_objects.exclude(is_published=False).filter(
            name__in=[obj.name for obj in categories])

        return render(request, "drevo/my_knowledge_grade.html", context)
