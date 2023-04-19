from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import TemplateView

from derzn.drevo.forms import RelationStatusesForm
from derzn.drevo.utils.preparing_relations import PreparingRelationsMixin


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
