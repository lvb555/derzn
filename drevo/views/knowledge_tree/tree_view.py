from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView

from drevo.models import Znanie


class KnowledgeTreeView(TemplateView):
    template_name = "drevo/knowledge_tree_view/tree.html"


class KnowledgeGraphView(TemplateView):
    template_name = "drevo/knowledge_tree_view/knowledge_graph.html"

    def get_context_data(self, **kwargs):
        idx = self.kwargs.get("id")
        context = super().get_context_data(**kwargs)
        knowledge = get_object_or_404(Znanie, id=idx)
        context["knowledge"] = knowledge
        return context
