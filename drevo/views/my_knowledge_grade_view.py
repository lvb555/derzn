from drevo.models.knowledge import Znanie
from drevo.models.knowledge_grade import KnowledgeGrade
from drevo.models.category import Category
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse


@login_required
def my_knowledge_grade(request) -> HttpResponse:
    """
    Страница "Мои оценки знания"
    """
    context = {}

    knowledges_grade = KnowledgeGrade.objects.prefetch_related("knowledge")\
                                             .exclude(knowledge__category=None)\
                                             .filter(user=request.user)
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
    return render(request, "drevo/my_knowledge_grade.html", context)
