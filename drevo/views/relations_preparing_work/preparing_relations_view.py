from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_http_methods
from django.urls import reverse_lazy, reverse
from django.views.generic import TemplateView
from drevo.models import Znanie, RelationStatuses, Relation, RelationshipTzTr, Tz, KnowledgeStatuses, Author, Tr
from drevo.forms import RelationStatusesForm, AdditionalKnowledgeForm
from drevo.utils.preparing_relations import PreparingRelationsMixin
from pip._vendor import requests


class PreparingRelationsCreateView(LoginRequiredMixin, TemplateView, PreparingRelationsMixin):
    """
        Страница подготовки связей.
        Этапы - Создание связей (create)
    """
    template_name = 'drevo/relations_preparing_page/preparing_relations_page.html'
    login_url = reverse_lazy('login')
    extra_context = {'stage_name': 'Создание связей'}

    def get_context_data(self, **kwargs):
        context = super(PreparingRelationsCreateView, self).get_context_data(**kwargs)
        context['knowledge'] = self.get_queryset(user=self.request.user, stage='create')
        form_data = {'stage': 'create'}
        context['statuses_form'] = RelationStatusesForm(**form_data)
        return context


class RelationCreatePageView(LoginRequiredMixin, TemplateView):
    """
        Страница создания связей
    """
    template_name = 'drevo/relations_preparing_page/relation_create_page.html'
    login_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = super(RelationCreatePageView, self).get_context_data(**kwargs)
        bz_pk = self.request.GET.get('base_kn')
        base_knowledge = get_object_or_404(Znanie, pk=bz_pk)
        context['base_knowledge'] = base_knowledge

        url = self.request.build_absolute_uri(reverse('get_required_tr'))
        resp = requests.get(url=url, params={'bz_id': bz_pk})
        rt_data = resp.json().get('required_tr')
        context['rt_data'] = [(type_data.get('id'), type_data.get('name')) for type_data in rt_data] if rt_data else []

        context['create_form'] = AdditionalKnowledgeForm()

        required_statuses = {
            'user': [('WORK_PRE', 'ПредСвязь в работе'), ('PRE_FIN', 'Завершенная ПредСвязь')],
            'expert': [('WORK', 'Связь в работе'), ('FIN', 'Завершенная Связь')]
        }
        context['relation_statuses'] = required_statuses.get('expert') if self.request.user.is_expert else required_statuses.get('user')
        return context


@login_required
@require_http_methods(['POST'])
@transaction.atomic
def relation_create_view(request):
    """
        Создание связи
    """
    req_data = request.POST
    bz = get_object_or_404(Znanie, pk=req_data.get('base_kn'))
    tr = get_object_or_404(Tr, pk=req_data.get('relation_type'))
    rz = get_object_or_404(Znanie, pk=req_data.get('related_knowledge'))
    rel_status = req_data.get('relation_status')
    user = request.user
    authors = Author.objects.filter(user_author=user)
    if authors.exists():
        author = authors.first()
    else:
        author = Author.objects.create(name=user.get_full_name, user_author=user)
    relation = Relation.objects.create(bz=bz, tr=tr, rz=rz, author=author, user=user)
    RelationStatuses.objects.create(relation=relation, status=rel_status, user=user)
    return redirect('preparing_relations_create_page')


@login_required
@require_http_methods(['GET'])
@transaction.atomic
def relation_delete_view(request):
    """
        Вьюшка удаления связи
    """
    bz = request.GET.get('bz_id')
    rz = request.GET.get('rz_id')
    Relation.objects.filter(bz_id=bz, rz_id=rz, user=request.user).delete()
    return redirect(request.META['HTTP_REFERER'])


class PreparingRelationsUpdateView(LoginRequiredMixin, TemplateView, PreparingRelationsMixin):
    """
        Страница подготовки связей.
        Этапы - Изменение связи (update)
    """
    template_name = 'drevo/relations_preparing_page/preparing_relations_page.html'
    login_url = reverse_lazy('login')
    extra_context = {'stage_name': 'Изменение связи'}

    def get_context_data(self, **kwargs):
        context = super(PreparingRelationsUpdateView, self).get_context_data(**kwargs)
        selected_status = self.request.GET.get('status')
        context['knowledge'] = self.get_queryset(user=self.request.user, stage='update', status=selected_status)
        context['selected_status'] = self.get_norm_stage_name(selected_status) if selected_status else 'Все'
        form_data = {'stage': 'update'}
        if selected_status:
            form_data['initial'] = {'status': selected_status}
        context['statuses_form'] = RelationStatusesForm(**form_data)
        return context


class PreparingRelationsExpertiseView(LoginRequiredMixin, TemplateView, PreparingRelationsMixin):
    """
        Страница подготовки связей.
        Этапы - Экспертиза ПредСвязи (expertise)
    """
    template_name = 'drevo/relations_preparing_page/preparing_relations_page.html'
    login_url = reverse_lazy('login')
    extra_context = {'stage_name': 'Экспертиза ПредСвязи'}

    def get_context_data(self, **kwargs):
        context = super(PreparingRelationsExpertiseView, self).get_context_data(**kwargs)
        selected_status = self.request.GET.get('status')
        context['knowledge'] = self.get_queryset(user=self.request.user, stage='expertise', status=selected_status)
        context['selected_status'] = self.get_norm_stage_name(selected_status) if selected_status else 'Все'
        form_data = {'stage': 'expertise'}
        if selected_status:
            form_data['initial'] = {'status': selected_status}
        context['statuses_form'] = RelationStatusesForm(**form_data)
        return context


class PreparingRelationsPublicationView(LoginRequiredMixin, TemplateView, PreparingRelationsMixin):
    """
        Страница подготовки связей.
        Этап - Публикация cвязей (publication)
    """
    template_name = 'drevo/relations_preparing_page/preparing_relations_page.html'
    login_url = reverse_lazy('login')
    extra_context = {'stage_name': 'Публикация cвязей'}

    def get_context_data(self, **kwargs):
        context = super(PreparingRelationsPublicationView, self).get_context_data(**kwargs)
        selected_status = self.request.GET.get('status')
        context['knowledge'] = self.get_queryset(user=self.request.user, stage='publication', status=selected_status)
        context['selected_status'] = self.get_norm_stage_name(selected_status) if selected_status else 'Все'
        form_data = {'stage': 'publication'}
        if selected_status:
            form_data['initial'] = {'status': selected_status}
        context['statuses_form'] = RelationStatusesForm(**form_data)
        return context
