from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import TemplateView
from django.views.decorators.http import require_http_methods
from drevo.forms import RelationStatusesForm, AdditionalKnowledgeForm
from drevo.utils.preparing_relations import PreparingRelationsMixin
from drevo.models import Relation, Znanie, Tr, RelationStatuses
from pip._vendor import requests


class PreparingRelationsUpdateView(LoginRequiredMixin, TemplateView, PreparingRelationsMixin):
    """
        Страница подготовки связей.
        Этап - Изменение связи (update)
    """
    template_name = 'drevo/relations_preparing_page/preparing_relations_page.html'
    login_url = reverse_lazy('login')
    extra_context = {'stage_name': 'Изменение связи', 'related_widgets': 'update delete'}

    def get_status_list(self):
        if self.request.user.is_expert:
            return [(None, '------'), ('WORK', 'Связь в работе'), ('FIN', 'Завершенная Связь')]
        return [(None, '------'), ('WORK_PRE', 'ПредСвязь в работе'), ('PRE_FIN', 'Завершенная ПредСвязь')]

    def get_form(self):
        selected_status = self.request.GET.get('status')
        form_data = {'statuses': self.get_status_list()}
        if selected_status:
            form_data['initial'] = {'status': selected_status}
        return RelationStatusesForm(**form_data)

    def get_context_data(self, **kwargs):
        context = super(PreparingRelationsUpdateView, self).get_context_data(**kwargs)
        selected_status = self.request.GET.get('status')
        context['knowledge'] = self.get_queryset(user=self.request.user, stage='update', status=selected_status)
        context['selected_status'] = self.get_norm_stage_name(selected_status) if selected_status else 'Все'
        context['statuses_form'] = self.get_form()
        return context


class RelationUpdatePageView(LoginRequiredMixin, TemplateView, PreparingRelationsMixin):
    """
        Страница обновления связей
    """
    template_name = 'drevo/relations_preparing_page/relation_update_page.html'
    login_url = reverse_lazy('login')
    extra_context = {'title': 'Обновление связи знаний', 'stage': 'update'}

    def get_context_data(self, **kwargs):
        context = super(RelationUpdatePageView, self).get_context_data(**kwargs)
        bz_pk, rz_pk = self.request.GET.get('bz'), self.request.GET.get('rz')
        context.update(self.get_relation_update_context(request=self.request, bz_pk=bz_pk, rz_pk=rz_pk))
        context['create_form'] = AdditionalKnowledgeForm()

        required_statuses = {
            'user': [('WORK_PRE', 'ПредСвязь в работе'), ('PRE_FIN', 'Завершенная ПредСвязь')],
            'expert': [('WORK', 'Связь в работе'), ('FIN', 'Завершенная Связь')]
        }
        context['relation_statuses'] = (
            required_statuses.get('expert') if self.request.user.is_expert else required_statuses.get('user')
        )
        return context


@login_required
@require_http_methods(['POST'])
@transaction.atomic
def relation_update_view(request, relation_pk):
    """
        Вьюшка обновления связи знаний
    """
    relation = get_object_or_404(Relation, pk=relation_pk)
    req_data = request.POST
    tr = get_object_or_404(Tr, pk=req_data.get('relation_type'))
    rz = get_object_or_404(Znanie, pk=req_data.get('related_knowledge'))
    rel_status = req_data.get('relation_status')
    change_statuses = {'WORK': 'FIN', 'WORK_PRE': 'PRE_FIN', 'FIN': 'WORK', 'PRE_FIN': 'WORK_PRE'}
    relation.tr = tr
    relation.rz = rz
    relation.save()
    RelationStatuses.objects.filter(relation=relation).update(status=change_statuses.get(rel_status))
    return redirect('preparing_relations_update_page')
