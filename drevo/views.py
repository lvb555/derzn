from django.views.generic import ListView, TemplateView, DetailView
from .models import Tz, Znanie


class DrevoListView(ListView):
    """
    выводит сущности Знание для заданной рубрики
    """
    template_name = 'drevo/type.html'
    model = Znanie
    context_object_name = 'znanie'

    def get_queryset(self):
        """
        формирует выборку из сущностей Знание для вывода
        """
        tz_pk = self.kwargs['pk']
        qs = Znanie.objects.filter(tz__pk=tz_pk)
        return qs

class DrevoView(TemplateView):
    """
    Выводит древо с иерархией видов знаний
    """
    template_name = 'drevo/drevo.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        """
        Передает данные в шаблон
        """
        context = super().get_context_data(**kwargs)
        # формирует список всех видов знаний
        ztypes = Tz.objects.all()
        context['ztypes'] = ztypes
        return context

class ZnanieDetailView(DetailView):
    """
    Выводит подробную информацию о сущности Знание
    """
    model = Znanie
    context_object_name = 'znanie'
    template_name = 'drevo/znanie_detail.html'
