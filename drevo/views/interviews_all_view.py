from django.shortcuts import render
from drevo.models.knowledge import Znanie
from drevo.models.relation import Relation
import datetime
from django.shortcuts import render
from drevo.models.author import Author
from drevo.models.category import Category
from drevo.models.knowledge import Znanie
from drevo.models.knowledge_kind import Tz

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
                    try:
                        list_period_interview = relation.rz.name.split('-')
                        the_end_of_period = list_period_interview[1]
                        print(the_end_of_period)
                        date_end = datetime.datetime.strptime(the_end_of_period, "%d.%m.%y")
                        if date_end < now - datetime.timedelta(days=1):
                            valid_interviews.append(interview)
                    except(ValueError):
                        list_period_interview = relation.rz.name.split(' - ')
                        the_end_of_period = list_period_interview[1]
                        print(the_end_of_period)
                        date_end = datetime.datetime.strptime(the_end_of_period, "%d.%m.%y")
                        if date_end < now - datetime.timedelta(days=1):
                            valid_interviews.append(interview)
        category_interviews.append((category, valid_interviews)) 

    return render(request, "drevo/interviews_all.html", {'categories': categories, 'interviews': interviews, 
    'valid_interviews': valid_interviews, 'now': now, 'date_end': date_end, 'category_interviews': category_interviews,
    'authors': authors}) 
