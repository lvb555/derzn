from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import Http404, get_object_or_404, render
from django.views.generic import TemplateView

from drevo.models.knowledge import Znanie
from drevo.models.knowledge_grade import KnowledgeGrade
from drevo.models.knowledge_grade_scale import KnowledgeGradeScale
from drevo.models.relation import Relation
from drevo.models.relation_grade import RelationGrade
from drevo.models.relation_grade_scale import RelationGradeScale
from drevo.utils.common import validate_parameter_int
from drevo.utils.knowledge_grader import KnowledgeGraderService


class KnowledgeFormView(LoginRequiredMixin, TemplateView):
    template_name = "drevo/knowledge_grade/knowledge_grade.html"
    partial_name = "drevo/knowledge_grade/score_card.html"

    def get_context_data(self, **kwargs):
        user = self.request.user
        knowledge = get_object_or_404(
            Znanie.objects.select_related("tz"), id=kwargs.get("pk")
        )
        # только для знаний, которые можно оценить
        if not knowledge.tz.can_be_rated:
            raise Http404

        context = super().get_context_data(**kwargs)
        context["title"] = "Оценка знания"
        context["knowledge"] = knowledge

        # ищем родительское знание, не факт, что правильно
        father_knowledge = Relation.objects.filter(rz=knowledge).first()
        if father_knowledge:
            context["father_knowledge"] = father_knowledge

        # обновляем кэш и дальше используем его
        KnowledgeGradeScale.validate_cache()
        RelationGradeScale.validate_cache()
        context["knowledge_scale"] = KnowledgeGradeScale.get_cache()
        context["relation_scale"] = RelationGradeScale.get_cache()

        variant = validate_parameter_int(
            self.request.GET.get("variant"), default=1, good_values=[1, 2]
        )
        context["variant"] = variant

        grader = KnowledgeGraderService(user, knowledge)
        proof_relations, grades = grader.do_calc(variant)

        context["proof_relations"] = proof_relations
        context.update(grades)

        return context

    def post(self, request, *args, **kwargs):
        """Возвращает только частичный рендер страницы с оценками
        для отображения с помощью htmx
        """
        user = request.user

        new_knowledge_grade = request.POST.get("knowledge_grade", None)
        new_relation_grade = request.POST.get("relation_grade", None)
        proof_relation = request.POST.get("relation", None)
        proof_knowledge = request.POST.get("knowledge", None)

        if (
            new_knowledge_grade
            and proof_knowledge
            and new_knowledge_grade != KnowledgeGradeScale.get_default_grade().id
        ):
            KnowledgeGrade.objects.update_or_create(
                knowledge_id=proof_knowledge,
                user=user,
                defaults={"grade_id": new_knowledge_grade},
            )

        if (
            new_relation_grade
            and proof_relation
            and new_relation_grade != RelationGradeScale.get_default_grade().id
        ):
            RelationGrade.objects.update_or_create(
                relation_id=proof_relation,
                user=user,
                defaults={"grade_id": new_relation_grade},
            )

        context = self.get_context_data(**kwargs)
        return render(request, self.partial_name, context)
