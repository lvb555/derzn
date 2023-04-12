from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from drevo.models import Znanie, RelationStatuses
from drevo.forms import RelationStatusesForm


class PreparingRelationsView(LoginRequiredMixin, TemplateView):
    """
        Страница подготовки связей.
        Этапы:
        - Создание связей (create)
        - Изменение связи (update)
        - Экспертизв ПредСвязи (expertise)
        - Публикация cвязей (publication)
    """
    template_name = 'drevo/preparing_relations_page.html'
    login_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = super(PreparingRelationsView, self).get_context_data(**kwargs)
        stage_name = self.request.GET.get('stage') if self.request.GET.get('stage') else 'create'
        context['stage'] = stage_name
        stage_names = {
            'create': 'Создание связей',
            'update': 'Изменение связи',
            'expertise': 'Экспертизв ПредСвязи',
            'publication': 'Публикация cвязей'
        }
        context['statuses_form'] = RelationStatusesForm(stage=stage_name)
        context['stage_name'] = stage_names.get(stage_name) if stage_name else 'Создание связей'

        context['knowledge'] = Znanie.objects.filter(is_published=True).all()[:50]

        selected_status = self.request.GET.get('status')
        context['selected_status'] = selected_status if selected_status else 'Все'
        return context
