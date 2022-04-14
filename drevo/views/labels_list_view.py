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
    queryset = Label.objects.annotate(zn_num=Count('znanie',
                                                   filter=Q(znanie__is_published=True))).\
        all().order_by('name')
