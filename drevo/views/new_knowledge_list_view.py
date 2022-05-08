import datetime

from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView
from django.views.generic.edit import FormMixin

from drevo.models import Znanie

from ..forms import DateNewForm
from loguru import logger

logger.add('logs/main.log',
           format="{time} {level} {message}", rotation='100Kb', level="ERROR")


class NewKnowledgeListView(ListView, FormMixin):
    """
    полный список недавно опубликованных знаний
    """
    template_name = 'drevo/new_knowledge.html'
    model = Znanie
    context_object_name = 'categorized_new_knowledges'
    # no practical use
    form_class = DateNewForm
    success_url = ''

    def get_queryset(self):
        date_form = DateNewForm(self.request.GET or None)
        date_for_new = datetime.date.today() - datetime.timedelta(days=7)
        if date_form.is_valid():
            year = date_form.cleaned_data.get('year')
            month = date_form.cleaned_data.get('month')
            day = date_form.cleaned_data.get('day')
            date_for_new = datetime.date(year, month, day)
        last_knldgs = Znanie.objects.filter(date__gte=date_for_new)
        ctgrs = [knldg.category for knldg in last_knldgs]
        nstd_l = {}
        for ctgr in ctgrs:
            nstd_l[ctgr] = []
        for n_k in last_knldgs:
            nstd_l[n_k.category].append(n_k)
        return nstd_l

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        _get = self.request.GET
        context['dform'] = DateNewForm(initial=_get.dict()) if not _get else DateNewForm(_get)
        return context
