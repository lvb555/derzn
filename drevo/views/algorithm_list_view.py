from django.views.generic import ListView
from ..models import Znanie, Tz
from loguru import logger

logger.add(
    "logs/main.log", format="{time} {level} {message}", rotation="100Kb", level="ERROR"
)


class AlgorithmListView(ListView):
    """
    выводит список алгоритмов
    """

    template_name = "drevo/all_algorithms.html"
    model = Znanie
    context_object_name = "all_algorithms"

    def get_queryset(self):
        algorithm_type = Tz.objects.get(name="Алгоритм")
        return Znanie.objects.filter(tz=algorithm_type, is_published=True)
