from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from drevo.models import Znanie, Tr
from django.db.models import Q


class RelationTypesView(TemplateView):
    """
        Страница "Вид связи"
    """
    template_name = 'drevo/relation_types_page.html'

    def get_context_data(self, **kwargs):
        context = super(RelationTypesView, self).get_context_data(**kwargs)
        rel_type = get_object_or_404(Tr, pk=self.kwargs.get('type_pk'))
        knowledge = (
            Znanie.objects
            .filter(
                Q(related__tr=rel_type) & Q(related__is_published=True),
                tz__is_systemic=False, is_published=True,
            )
        )
        context.update({'knowledge': knowledge, 'type_name': rel_type.name})
        return context
