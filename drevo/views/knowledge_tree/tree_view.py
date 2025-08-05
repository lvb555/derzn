from django.views.generic import TemplateView


class KnowledgeTreeView(TemplateView):
    template_name = "drevo/knowledge_tree_view/tree.html"
