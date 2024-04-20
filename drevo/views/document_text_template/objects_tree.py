from django.views.generic import TemplateView
from drevo.models import TemplateObject, Znanie, Turple
from drevo.forms import TemplateObjectForm, GroupForm
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
        objects = TemplateObject.objects.filter(Q(knowledge=document_knowledge, availability=0) | Q(user=self.request.user, availability=1) | Q(user=None, availability=1) | Q(availability=2))

        context['knowledge'] = document_knowledge
        context['objects'] = objects
        
        context['var_form'] = TemplateObjectForm(initial={'knowledge': document_knowledge.id})  # форма создания/изменения объектов
        context['var_form'].fields['turple'].queryset = Turple.objects.all()  # допустимые справочники
        
        context['var_form'].fields['connected_to'].queryset = objects

        context['group_form'] = GroupForm(initial={'knowledge': document_knowledge})
        context['group_form'].fields['parent'].queryset = objects

        return context
