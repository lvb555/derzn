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
        # possible to refactor with FormMixin
        # knowledge_later_than = self.request.GET.get('date_point')
        # if knowledge_later_than
        date_for_new = ''
        # if self.request.method == 'POST':
        self.dform = DateNewForm(self.request.GET)
        if self.dform.is_valid():
            day = self.dform.cleaned_data.get('day')
            month = self.dform.cleaned_data.get('month')
            year = self.dform.cleaned_data.get('year')
            date_for_new = datetime.date(year, month, day)
        new_knowledge_point = date_for_new or datetime.date.today() - datetime.timedelta(days=7)
        last_knldgs = Znanie.objects.filter(date__gt=new_knowledge_point)
        ctgrs = [knldg.category for knldg in last_knldgs]
        nstd_l = {}
        for ctgr in ctgrs:
            nstd_l[ctgr] = []
        for n_k in last_knldgs:
            nstd_l[n_k.category].append(n_k)
        return nstd_l

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['dform'] = self.dform if hasattr(self, 'dform') else DateNewForm()
        return context
