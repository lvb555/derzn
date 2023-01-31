from drevo.utils import get_group_users, get_average_base_grade, get_group_relations
from django.views.generic import TemplateView
from drevo.models.knowledge import Znanie
from django.shortcuts import Http404, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator

csrf_protected_method = method_decorator(csrf_protect)


class GroupKnowledgeView(TemplateView):
    template_name = 'drevo/group_knowledge_grade.html'

    def get(self, request, *args, **kwargs):
        knowledge = get_object_or_404(Znanie, id=kwargs.get('pk'))
        if knowledge.tz.can_be_rated:
            return super().get(request, *args, **kwargs)
        raise Http404

    def get_context_data(self, **kwargs):
        """
        Получение контекста
        """
        context = super().get_context_data(**kwargs)
        context['title'] = 'Оценка знания'

        user = self.request.user
        if user.is_authenticated:
            self.knowledge_id = self.kwargs.get('pk')
            knowledge = Znanie.objects.prefetch_related('base').get(
                id=self.knowledge_id)

            self.users = get_group_users(self.request, self.knowledge_id)
            base_grade, proof_base_grade, common_grade = \
                    get_average_base_grade(self.users, self.request, knowledge)

            context['base_grade'] = base_grade
            context['knowledge'] = knowledge

            proof_relations = knowledge.base.filter(
                tr__is_argument=True,
                rz__tz__can_be_rated=True,
            ).order_by('tr__name')

            context['proof_relations'] = get_group_relations(
                    self.request, self.users, proof_relations)

            context['proof_base_grade'] = proof_base_grade
            context['common_grade'] = common_grade

            context['count_users'] = len(self.users)
        return context 
