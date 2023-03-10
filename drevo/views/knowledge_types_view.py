from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from drevo.models import Znanie, Tz


class KnowledgeTypesView(TemplateView):
    """
        Страница "Вид знания"
    """
    template_name = 'drevo/knowledge_types_page.html'

    def get_context_data(self, **kwargs):
        context = super(KnowledgeTypesView, self).get_context_data(**kwargs)
        kn_type = get_object_or_404(Tz, pk=self.kwargs.get('type_pk'))
        knowledge = Znanie.objects.filter(tz_id=kn_type.id, is_published=True)
        context.update({'knowledge': knowledge, 'type_name': kn_type.name})
        return context
