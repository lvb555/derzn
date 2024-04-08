from django.shortcuts import HttpResponseRedirect, Http404, get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.generic import TemplateView

from drevo.models.knowledge import Znanie
from drevo.models.knowledge_grade import KnowledgeGrade
from drevo.models.knowledge_grade_scale import KnowledgeGradeScale
from drevo.models.relation import Relation
from drevo.models.relation_grade import RelationGrade
from drevo.models.relation_grade_scale import RelationGradeScale

csrf_protected_method = method_decorator(csrf_protect)


def knowledge_is_full_rated(knowledge, user, variant: int) -> bool:
    """Функция проверяет полностью ли оценено знание
    если вариант 1 - проверяет наличие оценки у знания
    если вариант 2 - проверяет наличие у знания аргументов и что они оценены
    Связи считаем всегда оцененными
    """
    if variant == 1:
        # есть оценка пользователя и она не системная (скрытая)
        grade = KnowledgeGrade.objects.filter(knowledge=knowledge, user=user).first()
        return grade and not grade.grade.is_hidden()

    elif variant == 2:
        # оценены все потомки и само знание
        proof_knowledge_lst = [
            relation.rz
            for relation in knowledge.base.filter(
                tr__is_argument=True,
                rz__tz__can_be_rated=True,
            ).select_related("rz")
        ]

        return all(map(lambda k: knowledge_is_full_rated(k, user, 2), proof_knowledge_lst)) and knowledge_is_full_rated(
            knowledge, user, 1
        )
    else:
        return True


class KnowledgeFormView(TemplateView):
    template_name = "drevo/knowledge_grade.html"

    def get(self, request, *args, **kwargs):
        knowledge = get_object_or_404(Znanie, id=kwargs.get("pk"))
        if knowledge.tz.can_be_rated:
            return super().get(request, *args, **kwargs)
        raise Http404

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Оценка знания"

        user = self.request.user
        if not user.is_authenticated:
            raise Http404

        knowledge = Znanie.objects.get(id=self.kwargs.get("pk"))
        context["knowledge"] = knowledge

        param_variant = self.request.GET.get("variant")
        if param_variant and param_variant.isdigit():
            variant = int(param_variant)
        else:
            variant = 1

        # получаем список аргументов
        proof_relations = list(
            knowledge.base.filter(
                tr__is_argument=True,
                rz__tz__can_be_rated=True,
            ).order_by("tr__name")
        )

        # считаем полностью ли оцененное знание
        for relation in proof_relations:
            relation.is_full_rated = knowledge_is_full_rated(relation.rz, user, variant)

        knowledge_is_rated = knowledge_is_full_rated(knowledge, user, 1)
        knowledge.is_full_rated = all([relation.is_full_rated for relation in proof_relations]) and knowledge_is_rated
        context["proof_relations"] = proof_relations

        # ищем родительское знание, не факт, что правильно
        father_knowledge = Relation.objects.filter(rz=knowledge).first()
        if father_knowledge:
            context["father_knowledge"] = father_knowledge

        # заполняем справочники для выпадающих списков
        context["knowledge_scale"] = KnowledgeGradeScale.objects.all()
        context["relation_scale"] = RelationGradeScale.objects.all()
        context["grade_scales"] = KnowledgeGradeScale.objects.all()

        # получаем оценки для знания
        common_grade_value, proof_base_value = knowledge.get_common_grades(request=self.request)

        # если нет оценки - преобразуем ее к 0-нет оценки
        if proof_base_value is None:
            proof_base_value = 0

        if common_grade_value is None:
            common_grade_value = 0

        context["proof_base_value"] = proof_base_value
        context["proof_base_grade"] = KnowledgeGradeScale.get_grade_object(proof_base_value)

        context["common_grade_value"] = common_grade_value
        context["common_grade"] = KnowledgeGradeScale.get_grade_object(common_grade_value)

        return context

    @csrf_protected_method
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise Http404

        knowledge_pk = kwargs.get("pk")

        variant = request.POST.get("variant")
        if variant:
            variant = variant.strip()
            self.request.path = f"{self.request.path}?variant={variant}"

        user = request.user

        # данных не будет, если значение в списке не выбрано (выбрано скрытое)
        if "base_knowledge_grade" not in request.POST:
            base_knowledge_grade = None
        else:
            base_knowledge_grade = request.POST["base_knowledge_grade"]

        # обновляем базовую оценку знания
        if base_knowledge_grade:
            KnowledgeGrade.objects.update_or_create(
                knowledge_id=knowledge_pk,
                user=user,
                defaults={"grade_id": base_knowledge_grade},
            )

        relation_rows = self.request.POST.getlist("relation_row")
        knowledge_grades = self.request.POST.getlist("knowledge_grade")
        relation_grades = self.request.POST.getlist("relation_grade")

        default_relation_grade_id = Relation.get_default_grade().pk
        default_knowledge_grade_id = Znanie.get_default_grade().pk

        # Обновляем ВСЕ данные? Зачем? Только одна строка же меняется
        for i, relation_id in enumerate(relation_rows):
            relation = Relation.objects.get(id=relation_id)

            # если пришло пустое значение - пропускаем
            # не сохраняем в базу значение по умолчанию
            if knowledge_grades[i] and knowledge_grades[i] != default_knowledge_grade_id:
                KnowledgeGrade.objects.update_or_create(
                    knowledge_id=relation.rz_id,
                    user=user,
                    defaults={"grade_id": knowledge_grades[i]},
                )

            # не сохраняем в базу значение по умолчанию
            if relation_grades[i] and relation_grades[i] != default_relation_grade_id:
                RelationGrade.objects.update_or_create(
                    relation_id=relation.id,
                    user=user,
                    defaults={"grade_id": relation_grades[i]},
                )

        return HttpResponseRedirect(self.request.path)
