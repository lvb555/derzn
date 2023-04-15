from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from drevo.models import Znanie, RelationStatuses
from drevo.forms import RelationStatusesForm
from drevo.utils.preparing_relations import PreparingRelationsMixin


class PreparingRelationsCreateView(LoginRequiredMixin, TemplateView, PreparingRelationsMixin):
    """
        Страница подготовки связей.
        Этапы - Создание связей (create)
    """
    template_name = 'drevo/preparing_relations_page.html'
    login_url = reverse_lazy('login')
    extra_context = {'stage_name': 'Создание связей'}

    def get_context_data(self, **kwargs):
        context = super(PreparingRelationsCreateView, self).get_context_data(**kwargs)
        selected_status = self.request.GET.get('status')
        user = self.request.user
        context['knowledge'] = self.get_queryset(user=user, stage='create', status=selected_status)
        context['selected_status'] = self.get_norm_stage_name(selected_status) if selected_status else 'Все'
        form_data = {'stage': 'create'}
        if selected_status:
            form_data['initial'] = {'status': selected_status}
        context['statuses_form'] = RelationStatusesForm(**form_data)
        return context


class PreparingRelationsUpdateView(LoginRequiredMixin, TemplateView, PreparingRelationsMixin):
    """
        Страница подготовки связей.
        Этапы - Изменение связи (update)
    """
    template_name = 'drevo/preparing_relations_page.html'
    login_url = reverse_lazy('login')
    extra_context = {'stage_name': 'Изменение связи'}

    def get_context_data(self, **kwargs):
        context = super(PreparingRelationsUpdateView, self).get_context_data(**kwargs)
        context['knowledge'] = Znanie.objects.filter(is_published=True).all()[:50]
        selected_status = self.request.GET.get('status')
        knowledge = self.get_queryset(stage='update', status=selected_status)
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
    template_name = 'drevo/preparing_relations_page.html'
    login_url = reverse_lazy('login')
    extra_context = {'stage_name': 'Экспертиза ПредСвязи'}

    def get_context_data(self, **kwargs):
        context = super(PreparingRelationsExpertiseView, self).get_context_data(**kwargs)
        context['knowledge'] = Znanie.objects.filter(is_published=True).all()[:50]
        selected_status = self.request.GET.get('status')
        knowledge = self.get_queryset(stage='expertise', status=selected_status)
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
    template_name = 'drevo/preparing_relations_page.html'
    login_url = reverse_lazy('login')
    extra_context = {'stage_name': 'Публикация cвязей'}

    def get_context_data(self, **kwargs):
        context = super(PreparingRelationsPublicationView, self).get_context_data(**kwargs)
        context['knowledge'] = Znanie.objects.filter(is_published=True).all()[:50]
        selected_status = self.request.GET.get('status')
        knowledge = self.get_queryset(stage='publication', status=selected_status)
        context['selected_status'] = self.get_norm_stage_name(selected_status) if selected_status else 'Все'
        form_data = {'stage': 'publication'}
        if selected_status:
            form_data['initial'] = {'status': selected_status}
        context['statuses_form'] = RelationStatusesForm(**form_data)
        return context
