from dataclasses import dataclass

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render

from drevo.models import FriendsInviteTerm, Message, Relation
from drevo.models.category import Category
from drevo.models.feed_messages import FeedMessage
from drevo.models.knowledge import Znanie
from drevo.models.knowledge_grade import KnowledgeGrade
from users.models import User
from users.views import access_sections


@dataclass
class KnowledgeRecord:
    """Вспомогательный класс для хранения информации о знаниях и их родителях.
        Используется для формирования дерева знаний с оценками
    """
    category: Category
    knowledge: Znanie
    grade: KnowledgeGrade
    children: list["KnowledgeRecord"]
    parents: list[Znanie]


def search_category(knowledge: Znanie) -> Category | None:
    """ Ищем категорию знания среди ближайших предков
        Если у ни одного из предков нет категории, то ищем у их предков и т.д.
        Сохраняем посещенные предки чтобы не получить рекурсию
    """

    children = [knowledge.pk]
    visited = set()
    visited.add(knowledge.pk)

    while children:
        parent_list = []
        for relation in (Relation.objects.filter(tr__is_argument=True, rz_id__in=children)
                                         .select_related('bz', 'bz__category')
                                         .only('bz__id', 'bz__category__id')):

            parent = relation.bz
            if parent.category:
                return parent.category
            elif parent.pk not in visited:
                visited.add(parent.pk)
                parent_list.append(parent.pk)

        children = parent_list

    return None


@login_required
def my_knowledge_grade(request, id) -> HttpResponse:
    """
    Страница "Мои оценки знания"
    Выводит дерево только тех знаний, на которые есть оценки пользователя
    Если знания связаны через Связь, то стараемся вывести их в иерархии
    (только если родительское знание есть в списке знаний с оценками)
    Если у знания несколько разных родительских знаний, то оно выведется только
    под одним из них (можно сказать под случайным родителем, первым в списке)
    Если знание без категории и без родителя:
     1. Сначала попытаемся определить категорию у родительских знаний, даже если они не оценивались
     2. Если не получилось, то появится дополнительная категория "Без категории"


    """
    if request.method == "GET":
        context = {}
        user = User.objects.filter(id=id).first()
        if not user:
            return HttpResponse(f"Пользователь id:{id} не найден")

        # далее заполняется контекст для показа в шапке профиля
        if user == request.user:
            # секции меню для показа в шапке профиля
            context["sections"] = access_sections(user)
            # Меню активность
            context["activity"] = [i for i in context["sections"] if i.startswith("Мои") or i.startswith("Моя")]
            context["link"] = "users:myprofile"
            invite_count = FriendsInviteTerm.objects.filter(recipient=request.user.id).count()
            context["invite_count"] = invite_count if invite_count else 0
            context["new_knowledge_feed"] = FeedMessage.objects.filter(recipient=user, was_read=False).count()
            context["new_messages"] = Message.objects.filter(recipient=user, was_read=False).count()
            context["new"] = int(context["new_knowledge_feed"]) + int(
                context["invite_count"] + int(context["new_messages"])
            )
        else:
            context["sections"] = [i.name for i in user.sections.all()]
            context["activity"] = [
                i.name for i in user.sections.all() if i.name.startswith("Мои") or i.name.startswith("Моя")
            ]
            context["link"] = "public_human"
            context["id"] = id

        context["pub_user"] = user

        # получаем все оценки знаний пользователя
        knowledges_grade = KnowledgeGrade.objects.prefetch_related("knowledge",
                                                                   "knowledge__category",
                                                                   "knowledge__tz",
                                                                   "knowledge__author").filter(user=user)

        knowledges_dict = {}
        categories = set()

        # заполняем словарь со знаниями
        for knowledge_grade in knowledges_grade:
            knowledge = knowledge_grade.knowledge
            category = knowledge.category
            parents = Relation.objects.filter(tr__is_argument=True, rz=knowledge).values_list("bz", flat=True)
            record = KnowledgeRecord(
                category=category, knowledge=knowledge, grade=knowledge_grade.grade, children=[], parents=list(parents)
            )

            knowledges_dict[knowledge.pk] = record

        knowledge_set = set(knowledges_dict.keys())
        knowledge_by_category = {}

        for record in knowledges_dict.values():
            is_orphan = True
            # если есть родители - пытаемся найти их и добавиться к ним
            if record.parents:
                # кандидаты - это знания, которые есть в нашем списке знаний и являются родителями данного знания
                candidates = set(record.parents) & knowledge_set
                if candidates:
                    # берем первого из кандидатов
                    parent = candidates.pop()
                    # и подключаем к нему наше знание
                    knowledges_dict[parent].children.append(record)
                    is_orphan = False

            if is_orphan:
                # если же не нашли для знания родителя - оно будет сразу после категории
                if not record.category:
                    record.category = search_category(record.knowledge)

                categories.add(record.category)
                knowledge_by_category.setdefault(record.category, []).append(record)

        context["zn_dict"] = knowledge_by_category

        # фильтруем категории - только наше дерево, без пустых листов
        category_set = set([i.id for i in categories if i])
        context["ztypes"] = Category.tree_objects.get_queryset_ancestors(
            Category.objects.filter(pk__in=category_set), include_self=True)

        return render(request, "drevo/knowledge_grade/my_knowledge_grade.html", context)
