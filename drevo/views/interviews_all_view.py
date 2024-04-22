from django.shortcuts import render
from drevo.models.relation import Relation
import datetime

def interviews_all(request):
    now = datetime.datetime.now()
    category_interviews = {}
    periods = Relation.objects.filter(tr__name="Период интервью").select_related('bz', 'bz__category')
    if periods:
        for period in periods:
            period_of_rel = period.rz.name.replace(" - ","-").split('-')
            the_2nd_part = period_of_rel[1]
            date_end = datetime.datetime.strptime(the_2nd_part, "%d.%m.%y")
            if date_end < now - datetime.timedelta(days=1):
                category = period.bz.category
                category_interviews.setdefault(category, []).append(period.bz)
    return render(request, "drevo/interviews_all.html", {
        'category_interviews': category_interviews.items()
    })

# def interviews_all(request):
#     now = datetime.datetime.now()
#     category_interviews = {}
#     periods = Relation.objects.filter(tr__name="Период интервью")
#     if periods:
#         for period in periods:
#             period_of_rel = period.rz.name.replace(" - ","-").split('-')
#             the_2nd_part = period_of_rel[1]
#             date_end = datetime.datetime.strptime(the_2nd_part, "%d.%m.%y")
#             if date_end < now - datetime.timedelta(days=1):
#                 category = period.bz.category
#                 category_interviews.setdefault(category, []).append(period.bz)
#     return render(request, "drevo/interviews_all.html", {
#         'category_interviews': category_interviews.items()
#     })

# def interviews_all(request):
#     now = datetime.datetime.now()
#     category_interviews = []
#     periods = Relation.objects.filter(tr__name="Период интервью")
#     if periods:
#         for period in periods:
#             period_of_rel = period.rz.name.replace(" - ","-").split('-')
#             the_2nd_part = period_of_rel[1]
#             date_end = datetime.datetime.strptime(the_2nd_part, "%d.%m.%y")
#             if date_end < now - datetime.timedelta(days=1):
#                 for category_interview in category_interviews:
#                     if category_interview[0] == period.bz.category:
#                         category_interview[1].append(period.bz)
#                         break
#                 else:
#                     category_interviews.append((period.bz.category, [period.bz]))
#     return render(request, "drevo/interviews_all.html", {
#     'category_interviews': category_interviews})

# from django.shortcuts import render
# from drevo.models.knowledge import Znanie
# from drevo.models.relation import Relation
# import datetime

# def interviews_all(request):
#     now = datetime.datetime.now()
#     interviews = Znanie.objects.filter(tz__name="Интервью", is_published=True)
#     category_interviews = []

#     for interview in interviews:
#         period = Relation.objects.filter(bz=interview, bz__category=interview.category, tr__name="Период интервью", ).first()
#         if period:
#             list_period_interview = period.rz.name.replace(" - ","-").split('-')
#             the_end_of_period = list_period_interview[1]
#             date_end = datetime.datetime.strptime(the_end_of_period, "%d.%m.%y")
#             if date_end < now - datetime.timedelta(days=1):
#                 for category_interview in category_interviews:
#                     if category_interview[0] == interview.category:
#                         category_interview[1].append(interview)
#                         break
#                 else:
#                     category_interviews.append((interview.category, [interview]))

#     return render(request, "drevo/interviews_all.html", {
#     'category_interviews': category_interviews})