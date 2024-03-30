from django.shortcuts import render
from drevo.models.knowledge import Znanie
from drevo.models.relation import Relation
import datetime
from datetime import timedelta
from django.shortcuts import redirect, render, get_object_or_404
from drevo.models.author import Author
from drevo.models.category import Category
from drevo.models.knowledge import Znanie
from drevo.models.knowledge_kind import Tz
from drevo.models.relation_type import Tr
from drevo.models.special_permissions import SpecialPermissions

def interviews_all(request):
    now = datetime.datetime.now()
    authors = Author.objects.all()
    categories = Category.objects.all()
    
    tz_id = Tz.objects.get(name="Интервью").id
    interviews = Znanie.objects.filter(tz_id=tz_id, is_published=True)
    category_interviews = []
    for category in categories:
        valid_interviews = []
        for interview in interviews:
            if interview.category == category:
                relation = Relation.objects.filter(bz=interview, tr__name="Период интервью").first()
                if relation:
                    list_period_interview = list(relation.rz.name)
                    the_end_of_period = list_period_interview[11:]
                    str_end_part = ''.join(the_end_of_period)
                    date_end = datetime.datetime.strptime(str_end_part, "%d.%m.%y")
                    if date_end < now - timedelta(days=1):
                        valid_interviews.append(interview)
        category_interviews.append((category, valid_interviews)) 

    return render(request, "drevo/interviews_all.html", {'categories': categories, 'interviews': interviews, 
    'valid_interviews': valid_interviews, 'now': now, 'date_end': date_end, 'category_interviews': category_interviews,
    'authors': authors})
    
# def Interviews_all(request):
#     now = datetime.datetime.now()
#     categories = Category.objects.all()
#     interviews = Znanie.objects.filter(tz__name="Интервью", is_published=True)
#     valid_interviews = {}
#     for category in categories:
#         valid_interviews[category] = []
#         for interview in interviews:
#             if interview.category == category:
#                 relation = Relation.objects.filter(bz=interview, tr__name="Период интервью").first()
#                 if relation:
#                     list_period_interview = list(relation.rz.name)
#                     the_end_of_period = list_period_interview[11:]
#                     str_end_part = ''.join(the_end_of_period)
#                     date_end = datetime.datetime.strptime(str_end_part, "%d.%m.%y")
#                     if date_end < now:
#                         valid_interviews[category].append(interview)
    

# def Interviews_all(request):
#     now = datetime.datetime.now()
#     categories = Category.objects.all()
#     interviews = Znanie.objects.filter(tz__name="Интервью", is_published=True)
#     valid_interviews = []
#     for category in categories:
#         categories_tr = Znanie.objects.filter(category__name=category)
#         for category_tr in categories_tr:
#             if category_tr:
#                 for interview in interviews:
#                     relation = Relation.objects.filter(bz=interview, tr__name="Период интервью").first()
#                     if relation:
#                         list_period_interview = list(relation.rz.name)
#                         the_end_of_period = list_period_interview[11:]
#                         str_end_part = ''.join(the_end_of_period)
#                         date_end = datetime.datetime.strptime(str_end_part, "%d.%m.%y")
#                         if date_end < now:
#                             valid_interviews.append(interview)



    # interviews = Znanie.objects.filter(tz__name="Интервью", is_published=True)
    # # interviews_tr = Relation.objects.filter(tr__name="Интервью", bz__tz__name= "Интервью")
    # relations = Relation.objects.all()
    # period_interviews = Relation.objects.filter(bz=interview, tr__name="Период интервью")
     
    # valid_interviews = []
   
    # for interview in interviews:
    #     for period_interview in period_interviews:
    #         if period_interview.bz.name == interview.name:
    #             list_period_interview = list(period_interview.rz.name)
    #             the_end_of_period = list_period_interview[11:]
    #             str_end = ''.join(the_end_of_period)
    #             # date_end = int(str_end)
    #             date_end = datetime.datetime.strptime(str_end, "%d.%m.%y")
    #             now = datetime.datetime.now()
    #             if date_end < now:
    #                 valid_interviews.append(interview)
                    
            
            
    
    # return render(request, "drevo/interviews_all.html", {'interviews': interviews,
    # 'the_2nd_part_of_period': the_2nd_part_of_period, 'days_of_period': days_of_period, 'months_of_period': months_of_period,
    # 'years_of_period': years_of_period, 'now': now})