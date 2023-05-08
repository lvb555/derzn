from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import TemplateView
from django.views.decorators.http import require_http_methods
from drevo.forms import RelationStatusesForm
from drevo.utils.preparing_relations import PreparingRelationsMixin
from drevo.models import Relation, Tr, Znanie, RelationStatuses
from drevo.forms import AdditionalKnowledgeForm, ZnImageFormSet


class PreparingRelationsExpertiseView(LoginRequiredMixin, TemplateView, PreparingRelationsMixin):
    """
        Страница подготовки связей.
        Этап - Экспертиза ПредСвязи (expertise)
    """
    template_name = 'drevo/relations_preparing_page/preparing_relations_page.html'
    login_url = reverse_lazy('login')
    extra_context = {'stage_name': 'Экспертиза ПредСвязи', 'related_widgets': 'expertise'}

    def get_status_list(self, knowledge):
        statuses_data = {
            'my': {'PRE_FIN': 'Завершенная ПредСвязь', 'PRE_EXP': 'Экспертизв ПредСвязи'},
            'competence': {'PRE_REJ': 'Отклоненная ПредСвязь', 'PRE_READY': 'Готовая ПредСвязь'}
        }
        statuses = self.get_stage_status_list('expertise', statuses_data, self.request.user, knowledge)
        return statuses

    def get_form(self, knowledge):
        selected_status = self.request.GET.get('status')
        statuses = self.get_status_list(knowledge)
        if not statuses:
            return None
        form_data = {'statuses': statuses}
        if selected_status:
            form_data['initial'] = {'status': selected_status}
        return RelationStatusesForm(**form_data)

    def get_context_data(self, **kwargs):
        context = super(PreparingRelationsExpertiseView, self).get_context_data(**kwargs)
        selected_status = self.request.GET.get('status')
        context['knowledge'] = self.get_queryset(user=self.request.user, stage='expertise', status=selected_status)
        context['selected_status'] = self.get_norm_stage_name(selected_status) if selected_status else 'Все'
        context['statuses_form'] = self.get_form(context.get('knowledge'))
        return context


class RelationsExpertisePageView(LoginRequiredMixin, TemplateView, PreparingRelationsMixin):
    """
        Страница экспертизы знания
    """
    template_name = 'drevo/relations_preparing_page/relation_update_page.html'
    login_url = reverse_lazy('login')
    extra_context = {'title': 'Экспертиза связи знаний', 'stage': 'expertise'}

    def get_context_data(self, **kwargs):
        context = super(RelationsExpertisePageView, self).get_context_data(**kwargs)
        bz_pk, rz_pk = self.request.GET.get('bz'), self.request.GET.get('rz')
        context.update(self.get_relation_update_context(bz_pk=bz_pk, rz_pk=rz_pk))
        context['create_form'] = AdditionalKnowledgeForm()
        context['image_form'] = ZnImageFormSet()

        required_statuses = {
            'PRE_READY': [
                ('PRE_EXP', 'Экспертиза ПредСвязи'),
                ('PRE_REJ', 'Отклонить ПредСвязь'),
                ('PRE_FIN', 'Завершить экспертизу ПредСвязи')
            ],
            'PRE_EXP': [
                ('PRE_EXP', 'Экспертиза ПредСвязи'),
                ('PRE_READY', 'Отказаться от экспертизы ПредСвязи'),
                ('PRE_REJ', 'Отклонить ПредСвязь'),
                ('PRE_FIN', 'Завершить экспертизу ПредСвязи')
            ],
            'PRE_REJ': [
                ('PRE_REJ', 'Отклоненная ПредСвязь'),
                ('PRE_EXP', 'Вернуть Предсвязь на экспертизу'),
            ],
            'PRE_FIN': [
                ('PRE_FIN', 'Завершенная ПредСвязь'),
                ('PRE_EXP', 'Вернуть Предсвязь на экспертизу'),
            ]
        }
        context['is_readonly'] = self.is_readonly_status(status=context.get('cur_status'), stage='expertise')
        context['relation_statuses'] = required_statuses.get(context.get('cur_status'))
        context['backup_url'] = reverse('preparing_relations_expertise_page')
        return context


@login_required
@require_http_methods(['POST'])
@transaction.atomic
def relation_expertise_view(request, relation_pk):
    """
        Вьюшка для экспертизы знания
    """
    relation = get_object_or_404(Relation, pk=relation_pk)
    req_data = request.POST
    if tr_pk := req_data.get('relation_type'):
        tr = get_object_or_404(Tr, pk=tr_pk)
        relation.tr = tr
    if rz_pk := req_data.get('related_knowledge'):
        rz = get_object_or_404(Znanie, pk=rz_pk)
        relation.rz = rz
    new_status = req_data.get('relation_status')
    relation.expert = request.user if new_status != 'PRE_READY' else None
    relation.save()

    relation_statuses = RelationStatuses.objects.filter(relation=relation)
    last_rel_status = None
    new_rel_status = None
    for rel_status in relation_statuses:
        if rel_status.is_active:
            last_rel_status = rel_status
            continue
        if rel_status.status == new_status:
            new_rel_status = rel_status
            continue

    if last_rel_status:
        last_rel_status.is_active = False
        last_rel_status.save()

    if new_rel_status:
        new_rel_status.is_active = True
        new_rel_status.user = request.user
        new_rel_status.save()
    else:
        RelationStatuses.objects.create(relation=relation, status=new_status, user=request.user)

    return redirect('preparing_relations_expertise_page')
