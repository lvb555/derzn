from drevo.utils import get_elements_tree, get_group_users, get_average_base_grade
from django.shortcuts import Http404, get_object_or_404
from django.views.generic import TemplateView
from drevo.models.knowledge import Znanie
from drevo.models.knowledge_grade_scale import KnowledgeGradeScale
from drevo.models.knowledge_grade import KnowledgeGrade


class GroupInfographicsView(TemplateView):
    template_name = 'drevo/group_infographics.html'

    def get(self, request, *args, **kwargs):
        self.knowledge = get_object_or_404(Znanie, id=kwargs['pk'])
        if self.knowledge.tz.can_be_rated:
            return super().get(request, *args, **kwargs)
        raise Http404

    def get_context_data(self, **kwargs):
        """
        Функция для получения контекста
        """
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            self.knowledge_id = self.kwargs.get('pk')
            knowledge = Znanie.objects.prefetch_related('base').get(
                id=self.knowledge_id)

            self.users = get_group_users(self.request, self.knowledge_id)
            base_grade, proof_base_grade, common_grade = \
                    get_average_base_grade(self.users, self.request, knowledge)

            context['base_grade'] = KnowledgeGradeScale.get_grade_object(
                base_grade.value)
            context['base_grade_value'] = base_grade.value
            context['knowledge'] = knowledge
            context['grade_scales'] = KnowledgeGradeScale.objects.all()

            proof_relations = knowledge.base.filter(
                tr__is_argument=True,
                rz__tz__can_be_rated=True,
            )

            context['proof_relations'] = proof_relations

            context['proof_base_value'] = proof_base_grade.value
            context['proof_base_grade'] = KnowledgeGradeScale.get_grade_object(
                proof_base_grade.value)
            context['common_grade_value'] = common_grade.value
            context['common_grade'] = KnowledgeGradeScale.get_grade_object(
                common_grade.value)

            self.index_element_tree = 0
            context['elements_tree'] = get_elements_tree(
                self.index_element_tree, self.request, proof_relations,
                is_group_knowledge=True, users=self.users)

            context['count_users'] = len(self.users)
        return context
