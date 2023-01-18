from drevo.utils import get_elements_tree
from django.shortcuts import Http404, get_object_or_404
from django.views.generic import TemplateView
from drevo.models.knowledge import Znanie
from drevo.models.knowledge_grade_scale import KnowledgeGradeScale
from drevo.models.knowledge_grade import KnowledgeGrade


class InfographicsView(TemplateView):
    template_name = 'drevo/infographics.html'

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
            knowledge = Znanie.objects.prefetch_related('base').get(
                id=self.kwargs.get('pk'))
            context["base_grade"] = KnowledgeGrade.objects.filter(
                knowledge=knowledge,
                user=self.request.user,
            ).first()
            context['knowledge'] = knowledge
            context['grade_scales'] = KnowledgeGradeScale.objects.all()

            proof_relations = knowledge.base.filter(
                tr__is_argument=True,
                rz__tz__can_be_rated=True,
            ).order_by('tr__name')

            context['proof_relations'] = proof_relations

            common_grade_value, proof_base_value = knowledge.get_common_grades(
                request=self.request)

            if proof_base_value is not None:
                context['proof_base_value'] = proof_base_value
                context['proof_base_grade'] = \
                    KnowledgeGradeScale.get_grade_object(proof_base_value)
            if common_grade_value is not None:
                context['common_grade_value'] = common_grade_value
                context['common_grade'] = KnowledgeGradeScale.get_grade_object(
                    common_grade_value)

            self.index_element_tree = 0
            context['elements_tree'] = get_elements_tree(
                self.index_element_tree, self.request, proof_relations)
        return context
