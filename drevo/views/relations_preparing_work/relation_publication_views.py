from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import TemplateView

from derzn.drevo.forms import RelationStatusesForm
from derzn.drevo.utils.preparing_relations import PreparingRelationsMixin


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
