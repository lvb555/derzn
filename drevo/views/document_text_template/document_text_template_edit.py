from django.views.generic import TemplateView
from drevo.models import Znanie, TemplateObject, Turple
from django.http import HttpResponseRedirect
from drevo.forms import ContentTemplate, TemplateObjectForm, TurpleForm, TurpleElementForm
from django.db.models import Q
from django.urls import reverse
import json


class DocumentTextTemplateEdit(TemplateView):

    """
    Редактирование и создание шаблона текста в документе
    """
    template_name = 'drevo/document_text_template/document_text_template.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        document_knowledge = Znanie.objects.get(id=context['doc_pk'])  # шаблон документа
        context['knowledge'] = document_knowledge

        context['var_form'] = TemplateObjectForm(initial={'knowledge': document_knowledge.id})  # форма создания/изменения объектов
        context['var_form'].fields['turple'].queryset = Turple.objects.all()  # допустимые справочники
        # допустимые главные переменные
        context['var_form'].fields['connected_to'].queryset = TemplateObject.objects.filter(Q(knowledge=document_knowledge, is_main=True) | Q(is_main=True, availability=1) | Q(is_main=True, availability=2))

        context['turple_form'] = TurpleForm(initial={'knowledge': document_knowledge.id})  # форма создания справочника

        context['turple_element_form'] = TurpleElementForm()  # форма создания элемента справочника

        context['object_structure_types'] = TemplateObject.available_sctructures  # типы структур объектов

        context['form'] = ContentTemplate(initial={'zn_pk': document_knowledge.id})  # форма шаблона текста

        knowledge = Znanie.objects.get(id=context['text_pk'])  # шаблон текста
        form = ContentTemplate(initial={
            'content': knowledge.content,
            'pk': knowledge.id,
            'zn_pk': document_knowledge.id})
        context['form'] = form
        
        # переменные, относящиеся к текущему шаблону
        context['objects'] = TemplateObject.objects.filter(Q(knowledge=document_knowledge) | Q(availability=1) | Q(availability=2))

        return context


        def post(self, request, **kwargs):
            template = ContentTemplate(request.POST)
            if template.is_valid():
                template.cleaned_data['pk'].content = template.cleaned_data['content']
                template.cleaned_data['pk'].save()
                return HttpResponse(json.dumps({'res':'ok'}, content_type='application/json'))
            else:
                return HttpResponse(json.dumps({'res':'err', 'errors':template.errors}, content_type='application/json'))
