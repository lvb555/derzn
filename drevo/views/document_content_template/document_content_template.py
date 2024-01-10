from django.views.generic import TemplateView
from drevo.models import Znanie, Var, Tz, Turple
from drevo.forms import ContentTemplate, VarForm, TurpleForm, TurpleElementForm
from django.db.models import Q
from django.urls import reverse
from django.http import HttpResponse
from django.core.exceptions import ValidationError
import json


class DocumentContentTemplate(TemplateView):

    """
    Редактирование и создание шаблона текста в документе
    """
    template_name = 'drevo/document_content_template.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        document_knowledge = Znanie.objects.get(id=self.request.GET['zn_id'])  # шаблон документа

        context['var_form'] = VarForm(initial={'knowledge': document_knowledge.id})  # форма создания/изменения объектов
        context['var_form'].fields['turple'].queryset = Turple.objects.filter(knowledge=document_knowledge)  # допустимые справочники

        # допустимые главные переменные
        context['var_form'].fields['connected_to'].queryset = Var.objects.filter(Q(knowledge=document_knowledge, is_main=True) | Q(is_main=True, is_global=True))

        context['turple_form'] = TurpleForm(initial={'knowledge': document_knowledge.id})  # форма создания справочника

        context['turple_element_form'] = TurpleElementForm()  # форма создания элемента справочника
        context['turple_element_form'].fields['var'].queryset = Var.objects.filter(knowledge=document_knowledge, structure=0)

        context['object_structure_types'] = Var.available_sctructures  # типы структур объектов


        # Ведется редактирование существующего шаблона?
        if 'id' not in self.request.GET:
            pass  # создание нового
        else:
            knowledge = Znanie.objects.get(id=self.request.GET['id'])  # шаблон текста
            context['form'] = ContentTemplate(initial={'zn_pk': document_knowledge.id})  # форма шаблона текста

        form = ContentTemplate(initial={
            'content': knowledge.content,
            'pk': knowledge.id,
            'zn_pk': document_knowledge.id})

        # переменные, относящиеся к текущему шаблону
        context['objects'] = Var.objects.filter(Q(knowledge=document_knowledge) | Q(is_global=True))
        context['form'] = form

        return context        
