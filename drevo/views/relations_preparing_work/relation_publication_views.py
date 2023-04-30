from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import TemplateView
from django.views.decorators.http import require_http_methods
from drevo.forms import RelationStatusesForm, AdditionalKnowledgeForm
from drevo.utils.preparing_relations import PreparingRelationsMixin
from drevo.models import Relation, Tr, Znanie, RelationStatuses


class PreparingRelationsPublicationView(LoginRequiredMixin, TemplateView, PreparingRelationsMixin):
    """
        Страница подготовки связей.
        Этап - Публикация cвязей (publication)
    """
    template_name = 'drevo/relations_preparing_page/preparing_relations_page.html'
    login_url = reverse_lazy('login')
    extra_context = {'stage_name': 'Публикация cвязей', 'related_widgets': 'publication'}

    def get_context_data(self, **kwargs):
        context = super(PreparingRelationsPublicationView, self).get_context_data(**kwargs)
        selected_status = self.request.GET.get('status')
        context['knowledge'] = self.get_queryset(user=self.request.user, stage='publication', status=selected_status)
        context['selected_status'] = self.get_norm_stage_name(selected_status) if selected_status else 'Все'
        statuses = [
            (None, '------'), ('PRE_FIN', 'Завершенная ПредСвязь'), ('PUB_PRE', 'Опубликованная ПредСвязь'),
            ('PRE_REJ', 'Отклоненная ПредСвязь'), ('FIN', 'Завершенная Связь'), ('PUB', 'Опубликованная Связь'),
            ('REJ', 'Отклоненная Связь')
        ]
        form_data = {'statuses': statuses}
        if selected_status:
            form_data['initial'] = {'status': selected_status}
        context['statuses_form'] = RelationStatusesForm(**form_data)
        return context


class RelationsPublicationPageView(LoginRequiredMixin, TemplateView, PreparingRelationsMixin):
    """
        Страница публикации связи
    """
    template_name = 'drevo/relations_preparing_page/relation_update_page.html'
    login_url = reverse_lazy('login')
    extra_context = {'title': 'Публикация связи знаний', 'stage': 'publication'}

    def get_context_data(self, **kwargs):
        context = super(RelationsPublicationPageView, self).get_context_data(**kwargs)
        bz_pk, rz_pk = self.request.GET.get('bz'), self.request.GET.get('rz')
        context.update(self.get_relation_update_context(bz_pk=bz_pk, rz_pk=rz_pk))
        context['create_form'] = AdditionalKnowledgeForm()

        required_statuses = {
            'PRE_FIN': [
                ('PUB_PRE', 'Опубликовать ПредСвязь'),
                ('PRE_REJ', 'Отклонить ПредСвязь'),
            ],
            'PUB_PRE': [
                ('PRE_REJ', 'Отклонить ПредСвязь'),
            ],
            'PRE_REJ': [
                ('PUB_PRE', 'Опубликовать ПредСвязь'),
            ],
            'FIN': [
                ('PUB', 'Опубликовать Связь'),
                ('REJ', 'Отклонить Связь')
            ],
            'PUB': [
                ('REJ', 'Отклонить Связь'),
            ],
            'REJ': [
                ('PUB', 'Опубликовать Связь'),
            ]
        }
        context['is_readonly'] = self.is_readonly_status(status=context.get('cur_status'), stage='publication')
        context['relation_statuses'] = required_statuses.get(context.get('cur_status'))
        context['backup_url'] = reverse('preparing_relations_publication_page')
        return context


@login_required
@require_http_methods(['POST'])
@transaction.atomic
def relation_publication_view(request, relation_pk):
    """
        Вьюшка для публикации связи
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
    relation.director = request.user
    relation.is_published = True if new_status in ('PUB_PRE', 'PUB',) else False
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

    return redirect('preparing_relations_publication_page')
