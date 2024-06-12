from django.shortcuts import render
from drevo.models.relation import Relation
from drevo.models.interview_answer_expert_proposal import InterviewAnswerExpertProposal
import datetime

def get_interviews_all():
    now = datetime.datetime.now()
    category_interviews = {}
    periods = Relation.objects.filter(tr__name="Период интервью").select_related('bz', 'bz__category')
    if periods:
        for period in periods:
            period_of_rel = period.rz.name.strip().replace(" ","").split('-')
            the_2nd_part = period_of_rel[1]
            
            date_end = datetime.datetime.strptime(the_2nd_part, "%d.%m.%y")
            if date_end < now - datetime.timedelta(days=1):
                category = period.bz.category
                category_interviews.setdefault(category, []).append(period.bz)
    return category_interviews.items()
def interviews_all(request):
    category_interviews = get_interviews_all() 
    return render(request, "drevo/interviews_all.html", {
        'category_interviews': category_interviews
    })

