from django.db.models import Count, Q
from django.views.generic import ListView
from ..models import Label
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

    def get_queryset(self):
        if tag_for_search := self.request.GET.get('tag_for_search'):
            return (
                Label.objects
                .annotate(zn_num=Count('znanie', filter=Q(znanie__is_published=True)))
                .filter(zn_num__gte=1, name__icontains=tag_for_search)
                .order_by('name')
            )
        return (
            Label.objects
            .annotate(zn_num=Count('znanie', filter=Q(znanie__is_published=True)))
            .filter(zn_num__gte=1)
            .order_by('name')
        )
