from django.views.generic import ListView
from ..models import Znanie, Tz
from loguru import logger

logger.add('logs/main.log',
           format="{time} {level} {message}", rotation='100Kb', level="ERROR")


class QuizListView(ListView):
    """
    выводит список теcтов
    """
    template_name = 'drevo/all_quizzes.html'
    model = Znanie
    context_object_name = 'all_tests'
    test_type = Tz.objects.get(name='Тест')
    queryset = Znanie.objects.filter(tz=test_type, is_published=True)