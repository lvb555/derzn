from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import Http404, get_object_or_404
from django.views.generic import TemplateView

from drevo.models.knowledge import Znanie
from drevo.models.knowledge_grade_scale import KnowledgeGradeScale
from drevo.utils.common import validate_parameter_int
from drevo.utils.knowledge_grader import KnowledgeGraderService


class InfographicsView(LoginRequiredMixin, TemplateView):
    template_name = "drevo/knowledge_grade/infographics.html"

    def get(self, request, *args, **kwargs):
        self.knowledge = get_object_or_404(Znanie, id=kwargs["pk"])
        if self.knowledge.tz.can_be_rated:
            return super().get(request, *args, **kwargs)
        raise Http404

    def get_context_data(self, **kwargs):
        """
        Функция для получения контекста
        """
        context = super().get_context_data(**kwargs)
        variant = validate_parameter_int(self.request.GET.get("variant"), default=-1, good_values=[1, 2])

        if variant == 2:
            context["title"] = "Инфографика. Общая оценка знания"
        else:
            context["title"] = "Инфографика. Оценка знания"

        context["variant"] = variant
        context["knowledge"] = self.knowledge

        grader = KnowledgeGraderService(self.request.user, self.knowledge)
        knowledge_tree = grader.get_tree(variant=variant)

        context["user_grade_text"] = knowledge_tree["user_knowledge_grade_text"]
        context["user_knowledge_grade_value"] = knowledge_tree["user_knowledge_grade_value"]
        context["user_knowledge_grade_id"] = knowledge_tree["user_knowledge_grade_id"]

        context["proof_grade_text"] = knowledge_tree["proof_grade_text"]
        context["proof_grade_value"] = knowledge_tree["proof_grade_value"]
        context["proof_grade_id"] = knowledge_tree["proof_grade_id"]

        context["common_grade_text"] = knowledge_tree["common_grade_text"]
        context["common_grade_value"] = knowledge_tree["common_grade_value"]
        context["common_grade_id"] = knowledge_tree["common_grade_id"]

        context["proof_relations"] = knowledge_tree["proof_relations"]

        context["knowledge_scale"] = KnowledgeGradeScale.get_cache()

        return context
