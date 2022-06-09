import datetime

from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView
from django.views.generic.edit import FormMixin

from drevo.models import Znanie

from ..forms import DatePickNewForm
from loguru import logger

# from ..forms.date_pick_form import DatePickNewForm

logger.add('logs/main.log',
           format="{time} {level} {message}", rotation='100Kb', level="ERROR")


class NewKnowledgeListView(ListView):
    """
    полный список недавно опубликованных знаний
    """
    model = Znanie
    template_name = 'drevo/new_knowledge_date_table.html'
    context_object_name = 'categorized_new_knowledges'


    def get_queryset(self):
        """по запросу из поля даты или за неделю
        :return Dict[category, List[knowledge]]"""
        date_form = DatePickNewForm(self.request.GET)
        date_for_new = datetime.date.today() - datetime.timedelta(days=7)
        if date_form.is_valid():
            date_for_new = date_form.cleaned_data.get('date')
        last_knldgs = Znanie.objects.filter(updated_at__gte=date_for_new,
                                            is_published=True, tz__is_systemic=False)
        # possible to ease hustle by using 'regroup' template kw
        ctgrs = [knldg.category for knldg in last_knldgs]
        nstd_l = {}
        ctgrs = set(ctgrs)
        for ctgr in ctgrs:
            nstd_l[ctgr] = []
        for n_k in last_knldgs:
            nstd_l[n_k.category].append(n_k)
        return nstd_l

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        _get = self.request.GET.dict()
        form_to_validate = DatePickNewForm(_get)
        if _get and form_to_validate.is_valid():
            context['datepick_form'] = DatePickNewForm(_get)
        else:
            context['datepick_form'] = DatePickNewForm()
        return context
