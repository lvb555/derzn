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