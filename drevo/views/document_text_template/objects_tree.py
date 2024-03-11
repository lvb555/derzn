from django.views.generic import TemplateView
from drevo.models import TemplateObject, Znanie
from django.db.models import Q



class ObjectsTree(TemplateView):
    """
        На странице строится дерево объектов для того, 
        чтобы выбрать объект для вставки в шаблон
    """
    template_name = 'drevo/document_text_template/objects_tree.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        document_knowledge = Znanie.objects.get(id=context['doc_pk'])
        context['knowledge'] = document_knowledge
        context['objects'] = TemplateObject.objects.filter(Q(knowledge=document_knowledge) | Q(availability=1) | Q(availability=2))

        return context
