import datetime

from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView
from django.views.generic.edit import FormMixin

from drevo.models import Znanie

from ..forms import DateNewForm


# @method_decorator(csrf_exempt, name='dispatch')
class NewKnowledgeListView(ListView, FormMixin):
    """
    полный список недавно опубликованных знаний
    """
    template_name = 'drevo/new_knowledge.html'
    model = Znanie
    context_object_name = 'categorized_new_knowledges'
    form_class = DateNewForm
    success_url = ''


    def get_queryset(self):
        # possible to refactor with FormMixin
        # knowledge_later_than = self.request.GET.get('date_point')
        # if knowledge_later_than
        # self.new_date = datetime.date.today() - datetime.timedelta(days=7)
        # date_form = DateNewForm(self.request.GET)
        date_for_new = datetime.date.today() - datetime.timedelta(days=7)
        self.dform = DateNewForm(self.request.GET or None)
        # print(self.dform)
        # print(self.request.GET)
        # date_form = self.get_form()
        # if date_form.is_valid:
        # year = date_form.cleaned_data.get('year')
        # month = date_form.cleaned_data.get('month')
        # day = date_form.cleaned_data.get('day')
        # year = date_form.
        if self.dform.is_valid():
            day = self.dform.cleaned_data.get('day')
            month = self.dform.cleaned_data.get('month')
            year = self.dform.cleaned_data.get('year')
            # print(date_form)
            # print(date_form.year)
            # date_for_new = datetime.date(date_form.year, date_form.month, date_form.day)
            date_for_new = datetime.date(year, month, day)
            # self.new_date = date_for_new
            # print('shouldn`t')
        # else:
            # print(self.dform.errors)
            # print(self.dform)
        #     self.form_invalid(form=self.dform)
        #     date_for_new = self.new_date
        new_knowledge_point = date_for_new  # or datetime.date.today() - datetime.timedelta(days=7)
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
        # print(self.dform)
        # print(self.request.GET)
        # print(self.request.POST)
        # print(self.new_date or 'eroor')
        _get = self.request.GET
        context['efform'] = DateNewForm(_get)
        context['dform'] = DateNewForm(initial=_get.dict()) if not _get else DateNewForm(_get)
        # print('valid w data:', context['efform'].is_valid())
        # print(type(context['efform']))
        # print(context['efform'])
        #
        # print('errors on dated:', context['efform'].errors)
        # print(context['dform'])
        # print('errors on new:', context['dform'].errors)
        # print('h_e new', context['dform'].has_error('day'))
        # print(_get)
        return context

    # def post(self, request):
    # self.object_list = self.get_queryset()
    # self.
    # if self.form_valid()
    # return HttpResponseRedirect(self.request.path_info, )
