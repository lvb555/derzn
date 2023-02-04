from drevo.models.knowledge import Znanie
from drevo.models.knowledge_grade import KnowledgeGrade
from drevo.models.category import Category
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from users.models import User, MenuSections
import copy



def my_knowledge_grade(request, id) -> HttpResponse:
    """
    Страница "Мои оценки знания"
    """
    if request.method == 'GET':
        context = {}
        user = User.objects.filter(id=id).first()
        if user is not None:
            if user == request.user:
                context['sections'] = [i.name for i in MenuSections.objects.all()]
                context['activity'] = [i.name for i in MenuSections.objects.all() if i.name.startswith('Мои') or
                                       i.name.startswith('Моя')]
                context['link'] = 'users:myprofile'
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
