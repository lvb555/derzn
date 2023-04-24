from django.db.models import Count, Q
from django.views.generic import ListView
from ..models import Label
from loguru import logger


logger.add('logs/main.log',
           format="{time} {level} {message}", rotation='100Kb', level="ERROR")


class LabelsListView(ListView):
    """
    выводит список меток
    """
    template_name = 'drevo/labels.html'
    model = Label
    context_object_name = 'labels'
    paginate_by = 25

    def get_queryset(self):
        tag_sorted = self.request.GET.get('order')
        have_to_be_sorted = 'name'
        if tag_sorted:
            if tag_sorted == '-count':
                have_to_be_sorted = 'zn_num'
            else:
                have_to_be_sorted = '-zn_num'
        if tag_for_search := self.request.GET.get('tag_for_search'):
            return (
                Label.objects
                .annotate(zn_num=Count('znanie', filter=Q(znanie__is_published=True)))
                .filter(zn_num__gte=1, name__icontains=tag_for_search)
                .order_by(have_to_be_sorted)
            )
        return (
            Label.objects
            .annotate(zn_num=Count('znanie', filter=Q(znanie__is_published=True)))
            .filter(zn_num__gte=1)
            .order_by(have_to_be_sorted)
        )

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        if tag_for_search := self.request.GET.get('tag_for_search'):
            context['tag_for_search'] = tag_for_search
        return context