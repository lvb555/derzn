import datetime

from django.views.generic import ListView

from drevo.models import Znanie

from ..forms import DateNewForm


class NewKnowledgeListView(ListView):
    """
    полный список недавно опубликованных знаний
    """
    template_name = 'drevo/new_knowledge.html'
    model = Znanie
    context_object_name = 'categorized_new_knowledges'

    def get_queryset(self):
        # knowledge_later_than = self.request.GET.get('date_point')
        # if knowledge_later_than

        last_knldgs = Znanie.objects.filter(date__gt=datetime.date.today() - datetime.timedelta(days=7))
        ctgrs = [knldg.category for knldg in last_knldgs]
        nstd_l = {}
        for ctgr in ctgrs:
            nstd_l[ctgr] = []
        for n_k in last_knldgs:
            nstd_l[n_k.category].append(n_k)
        return nstd_l

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['dform'] = DateNewForm()
        return context
