from django.views.generic import TemplateView
from drevo.models import Znanie, TemplateObject, Turple
from django.http import HttpResponse
from drevo.forms import ContentTemplate, TemplateObjectForm
from django.db.models import Q
import json


class DocumentTextTemplateEdit(TemplateView):

    """
    Редактирование и создание шаблона текста в документе
    """
    template_name = 'drevo/document_text_template/document_text_template.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not self.request.user.is_authenticated:
            return context

        document_knowledge = Znanie.objects.get(id=context['doc_pk'])  # шаблон документа
        objects = TemplateObject.objects.filter(Q(knowledge=document_knowledge, availability=0) |  Q(user=self.request.user, availability=1) | Q(user=None, availability=1) | Q(availability=2))

        context['var_form'] = TemplateObjectForm(initial={'knowledge': document_knowledge.id})  # форма создания/изменения объектов
        context['var_form'].fields['turple'].queryset = Turple.objects.all()  # допустимые справочники
        # допустимые главные переменные
        context['var_form'].fields['connected_to'].queryset = objects

        context['object_structure_types'] = TemplateObject.available_sctructures  # типы структур объектов

        knowledge = Znanie.objects.get(id=context['text_pk'])  # шаблон текста
        form = ContentTemplate(initial={
            'content': knowledge.content,
            'pk': knowledge.id,
            'zn_pk': document_knowledge.id})
        context['form'] = form

        # переменные, относящиеся к текущему шаблону
        context['objects'] = objects
        
        context['knowledge'] = document_knowledge

        return context

        def post(self, request, **kwargs):
            template = ContentTemplate(request.POST)
            if template.is_valid():
                template.cleaned_data['pk'].content = template.cleaned_data['content']
                template.cleaned_data['pk'].save()
                return JsonResponse({'res': 'ok'})
            else:
                return JsonResponse({'res': 'err', 'errors': template.errors})
