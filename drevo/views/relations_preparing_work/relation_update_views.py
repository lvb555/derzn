from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import TemplateView
from django.views.decorators.http import require_http_methods
from drevo.forms import RelationStatusesForm, AdditionalKnowledgeForm, ZnImageFormSet
from drevo.utils.preparing_relations import PreparingRelationsMixin
from drevo.models import Relation, Znanie, Tr, RelationStatuses


class PreparingRelationsUpdateView(LoginRequiredMixin, TemplateView, PreparingRelationsMixin):
    """
        Страница подготовки связей.
        Этап - Изменение связи (update)
    """
    template_name = 'drevo/relations_preparing_page/preparing_relations_page.html'
    login_url = reverse_lazy('login')
    extra_context = {'stage_name': 'Изменение связи', 'related_widgets': 'update delete'}

    def get_status_list(self):
        statuses_data = {
            'WORK_PRE': 'ПредСвязь в работе',
            'PRE_READY': 'Готовая ПредСвязь',
        }
        if self.request.user.is_expert:
            statuses_data.setdefault('WORK', 'Связь в работе')
            statuses_data.setdefault('FIN', 'Завершенная Связь')

        statuses = self.get_stage_status_list('update', statuses_data, self.request.user)
        return statuses

    def get_form(self):
        selected_status = self.request.GET.get('status')
        statuses = self.get_status_list()
        if not statuses:
            return None
        form_data = {'statuses': statuses}
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
        context.update(self.get_relation_update_context(bz_pk=bz_pk, rz_pk=rz_pk))
        context['create_form'] = AdditionalKnowledgeForm()
        context['image_form'] = ZnImageFormSet()

        required_statuses = {
            'WORK_PRE': [
                ('WORK_PRE', 'ПредСвязь в работе'),
                ('PRE_READY', 'Готовая ПредСвязь'),
            ],
            'PRE_READY': [
                ('PRE_READY', 'Готовая ПредСвязь'),
                ('WORK_PRE', 'ПредСвязь в работе'),
            ],
            'WORK': [
                ('WORK', 'Связь в работе'),
                ('FIN', 'Завершенная Связь'),
            ],
            'FIN': [
                ('FIN', 'Завершенная Связь'),
                ('WORK', 'Связь в работе'),
            ],
        }
        context['is_readonly'] = self.is_readonly_status(status=context.get('cur_status'), stage='update')
        context['relation_statuses'] = required_statuses.get(context.get('cur_status'))
        context['backup_url'] = reverse('preparing_relations_update_page')
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
    if tr_pk := req_data.get('relation_type'):
        tr = get_object_or_404(Tr, pk=tr_pk)
        relation.tr = tr
    if rz_pk := req_data.get('related_knowledge'):
        rz = get_object_or_404(Znanie, pk=rz_pk)
        relation.rz = rz
    new_status = req_data.get('relation_status')
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

    return redirect('preparing_relations_update_page')
