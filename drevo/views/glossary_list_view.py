
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
    paginate_by = 20

    def get_queryset(self):
        way_of_sorting = self.request.GET.get('order')
        if not way_of_sorting:
            way_of_sorting = 'name'
        if search_data := self.request.GET.get('glossary_term_for_search'):
            return (
                GlossaryTerm.objects
                .filter(is_published=True, name__icontains=search_data).order_by(way_of_sorting)
            )
        return GlossaryTerm.objects.filter(is_published=True).order_by(way_of_sorting)

    def get_context_data(self, *, object_list=None, **kwargs):
        """
        Контекст, передаваемый в шаблон
        """
        context = super().get_context_data(**kwargs)
        if self.request.GET.get('order') == '-name':
            context['ordering'] = ['По алфавиту (Я-А)', '-name']
        else:
            context['ordering'] = ['По алфавиту (А-Я)', 'name']
        if glossary_term_for_search := self.request.GET.get('glossary_term_for_search'):
            context['glossary_term_for_search'] = glossary_term_for_search
        return context
