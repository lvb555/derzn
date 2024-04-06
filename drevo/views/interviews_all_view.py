from django.shortcuts import render
from django.db.models import Prefetch
from drevo.models.knowledge import Znanie
from drevo.models.relation import Relation
import datetime
from drevo.models.author import Author
from drevo.models.category import Category

def interviews_all(request):
    now = datetime.datetime.now()
    authors = Author.objects.all()
    interviews_prefetch = Prefetch(
        'znanie_set',
        queryset=Znanie.objects.filter(tz__name="Интервью", is_published=True),
        to_attr='interviews'
    )
    categories = Category.objects.filter(is_published=True).prefetch_related(interviews_prefetch)

    category_interviews = []
    for category in categories:
        valid_interviews = []
        for interview in category.interviews:
            period = Relation.objects.filter(bz=interview, tr__name="Период интервью").first()
            if period:
                list_period_interview = period.rz.name.replace(" - ", "-").split('-')
                the_end_of_period = list_period_interview[1]
                date_end = datetime.datetime.strptime(the_end_of_period, "%d.%m.%y")
                if date_end < now - datetime.timedelta(days=1):
                    valid_interviews.append(interview)
        if valid_interviews:
            category_interviews.append((category, valid_interviews))
    return render(request, "drevo/interviews_all.html", {'categories': categories, 
    'category_interviews': category_interviews, 'authors': authors})