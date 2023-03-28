from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from drevo.models import Znanie, Tz
from django.db.models import Q


class KnowledgeTypesView(TemplateView):
    """
        Страница "Вид знания"
    """
    template_name = 'drevo/knowledge_types_page.html'

    def get_context_data(self, **kwargs):
        context = super(KnowledgeTypesView, self).get_context_data(**kwargs)
        kn_type = get_object_or_404(Tz, pk=self.kwargs.get('type_pk'))
        knowledge = (
            Znanie.objects
            .filter(
                Q(category__is_published=True) | Q(related__isnull=False),
                tz_id=kn_type.id, is_published=True,
            )
        )
        context.update({'knowledge': knowledge, 'type_name': kn_type.name})
        return context
