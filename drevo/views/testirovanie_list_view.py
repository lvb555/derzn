from django.views.generic import ListView
from ..models import Znanie, Tz
from loguru import logger

logger.add('logs/main.log',
           format="{time} {level} {message}", rotation='100Kb', level="ERROR")


class TestirovanieListView(ListView):
    """
    выводит список теcтов
    """
    template_name = 'drevo/all_tests.html'
    model = Znanie
    context_object_name = 'all_tests'
    queryset = Znanie.objects.filter(is_published=True,tz_id=21)