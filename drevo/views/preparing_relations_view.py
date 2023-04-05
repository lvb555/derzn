from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import TemplateView


class PreparingRelationsView(LoginRequiredMixin, TemplateView):
    """
        Страница подготовки связей
    """
    template_name = 'drevo/preparing_relations_page.html'
    login_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = super(PreparingRelationsView, self).get_context_data(**kwargs)
        context['title'] = ''
        context['step_name'] = ''
        context['selected_status'] = ''
        return context
