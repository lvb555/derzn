
from django.views.generic import ListView
from ..models import GlossaryTerm
from ..models import GlossaryTerm
from loguru import logger

logger.add('logs/main.log',
           format="{time} {level} {message}", rotation='100Kb', level="ERROR")


class GlossaryListView(ListView):
    """
    выводит список терминов глоссария
    """
    template_name = 'drevo/glossary.html'
    model = GlossaryTerm
    context_object_name = 'glossary_terms'
    queryset = GlossaryTerm.objects.filter(is_published=True)
