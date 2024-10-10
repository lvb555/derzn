from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import TemplateView

from drevo.forms import AdditionalKnowledgeForm, ZnImageFormSet
from drevo.models import Znanie
from drevo.utils.preparing_relations import PreparingRelationsMixin


class CreateParticipationView(LoginRequiredMixin, TemplateView, PreparingRelationsMixin):
    template_name = 'drevo/create_participation.html'
    login_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = super(CreateParticipationView, self).get_context_data(**kwargs)
        bz_pk = self.request.GET.get('base_kn')
        backup_url = self.request.GET.get('backup')
        base_knowledge = get_object_or_404(Znanie, pk=bz_pk)
        context['base_knowledge'] = base_knowledge
        context['create_form'] = AdditionalKnowledgeForm()
        context['image_form'] = ZnImageFormSet()

        required_statuses = {
            'user': [('WORK_PRE', 'ПредСвязь в работе'), ('PRE_READY', 'Готовая ПредСвязь')],
            'expert': [('WORK', 'Связь в работе'), ('FIN', 'Завершенная Связь')]
        }
        user_is_expert = self.check_competence(self.request.user, base_knowledge)
        context['relation_statuses'] = (
            required_statuses.get('expert') if user_is_expert else required_statuses.get('user')
        )
        context['backup_url'] = backup_url

        return context