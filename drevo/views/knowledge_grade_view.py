from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import Http404, get_object_or_404, render
from django.views.generic import TemplateView

from drevo.models import SettingsOptions
from drevo.models.knowledge import Znanie
from drevo.models.knowledge_grade import KnowledgeGrade
from drevo.models.knowledge_grade_scale import KnowledgeGradeScale
from drevo.models.relation import Relation
from drevo.models.relation_grade import RelationGrade
from drevo.models.relation_grade_scale import RelationGradeScale
from drevo.utils.common import validate_parameter_int, get_user_parameter
from drevo.utils.knowledge_grader import KnowledgeGraderService


class KnowledgeFormView(LoginRequiredMixin, TemplateView):
    template_name = "drevo/knowledge_grade/knowledge_grade.html"
    partial_name = "drevo/knowledge_grade/score_card.html"
    # идентификатор параметра пользователя, в котором хранится вариант расчета
    variant_user_parameter = SettingsOptions.Option.SCORE_VARIANT

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

        # вариант оценки знания (1 или 2) берем из POST, если в нем нет - из GET,
        # если нет - то из настроек пользователя, если и там нет - то 1
        if self.request.POST.get("variant"):
            variant = validate_parameter_int(
                self.request.POST.get("variant"), default=-1, good_values=[1, 2]
            )
        else:
            variant = validate_parameter_int(
                self.request.GET.get("variant"), default=-1, good_values=[1, 2]
            )
        # если параметр -1 (то есть нам его не передали или он неправильный), то берем из настроек пользователя
        if variant == -1:
            user_parameter = get_user_parameter(user, self.variant_user_parameter)
            # так как значение параметра 0 и 1 - прибавляем 1 к значению
            variant = user_parameter + 1 if user_parameter else 1

        context["variant"] = variant

        grader = KnowledgeGraderService(user, knowledge)
        proof_relations, grades = grader.do_calc(variant)

        context["proof_relations"] = proof_relations
        context.update(grades)

        return context

    def htmx_page(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return render(request, self.partial_name, context)

    def get(self, request, *args, **kwargs):
        # если это htmx запрос
        if request.headers.get("Hx-Request", False):
            return self.htmx_page(request, *args, **kwargs)

        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Возвращает только частичный рендер страницы с оценками
        для отображения с помощью htmx
        """
        user = request.user

        new_knowledge_grade = request.POST.get("knowledge_grade", None)
        new_relation_grade = request.POST.get("relation_grade", None)
        proof_relation = request.POST.get("relation", None)
        proof_knowledge = request.POST.get("knowledge", None)

        # если поменялась оценка знания
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

        # если поменялась оценка связи
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

        return self.htmx_page(request, *args, **kwargs)
