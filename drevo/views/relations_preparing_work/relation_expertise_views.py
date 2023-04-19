from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import TemplateView

from drevo.forms import RelationStatusesForm
from drevo.utils.preparing_relations import PreparingRelationsMixin


class PreparingRelationsExpertiseView(LoginRequiredMixin, TemplateView, PreparingRelationsMixin):
    """
        Страница подготовки связей.
        Этап - Экспертиза ПредСвязи (expertise)
    """
    template_name = 'drevo/relations_preparing_page/preparing_relations_page.html'
    login_url = reverse_lazy('login')
    extra_context = {'stage_name': 'Экспертиза ПредСвязи'}

    def get_context_data(self, **kwargs):
        context = super(PreparingRelationsExpertiseView, self).get_context_data(**kwargs)
        selected_status = self.request.GET.get('status')
        context['knowledge'] = self.get_queryset(user=self.request.user, stage='expertise', status=selected_status)
        context['selected_status'] = self.get_norm_stage_name(selected_status) if selected_status else 'Все'
        statuses = [
            (None, '------'), ('PRE_FIN', 'Завершенная ПредСвязь'), ('PRE_EXP', 'Экспертизв ПредСвязи'),
            ('PRE_REJ', 'Отклоненная ПредСвязь'), ('PRE_READY', 'Готовая ПредСвязь')
        ]
        form_data = {'statuses': statuses}
        if selected_status:
            form_data['initial'] = {'status': selected_status}
        context['statuses_form'] = RelationStatusesForm(**form_data)
        return context
