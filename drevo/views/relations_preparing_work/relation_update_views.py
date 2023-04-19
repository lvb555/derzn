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


class RelationUpdatePageView(LoginRequiredMixin, TemplateView):
    """
        Страница обновления связей
    """
    template_name = 'drevo/relations_preparing_page/relation_update_page.html'
    login_url = reverse_lazy('login')

    def get_require_tr(self, bz_pk: int):
        url = self.request.build_absolute_uri(reverse('get_required_tr'))
        resp = requests.get(url=url, params={'bz_id': bz_pk})
        rt_data = resp.json().get('required_tr')
        return [(type_data.get('id'), type_data.get('name')) for type_data in rt_data] if rt_data else []

    def get_require_rz(self, bz_pk: int, tr_pk: int):
        url = self.request.build_absolute_uri(reverse('get_required_rz'))
        resp = requests.get(url=url, params={'bz_id': bz_pk, 'tr_id': tr_pk})
        rz_data = resp.json().get('required_rz')
        return [(rz.get('id'), rz.get('name')) for rz in rz_data] if rz_data else []

    def check_rz(self, rz_pk: int):
        url = self.request.build_absolute_uri(reverse('check_related'))
        resp = requests.get(url=url, params={'rz_id': rz_pk})
        return resp.json()

    def get_context_data(self, **kwargs):
        context = super(RelationUpdatePageView, self).get_context_data(**kwargs)
        bz_pk, rz_pk = self.request.GET.get('bz'), self.request.GET.get('rz')
        relation = Relation.objects.select_related('bz', 'rz').filter(bz_id=bz_pk, rz_id=rz_pk).first()
        context['relation'] = relation
        context['rz_param'] = self.check_rz(rz_pk=rz_pk)
        context['rt_data'] = self.get_require_tr(bz_pk)
        context['rz_data'] = self.get_require_rz(bz_pk=bz_pk, tr_pk=relation.tr_id)
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
