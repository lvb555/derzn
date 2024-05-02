import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F, Count, Q, FilteredRelation, OuterRef, Subquery, Exists
from django.shortcuts import HttpResponseRedirect, Http404, get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.generic import TemplateView

from drevo.models import Tr
from drevo.models.knowledge import Znanie
from drevo.models.knowledge_grade import KnowledgeGrade
from drevo.models.knowledge_grade_scale import KnowledgeGradeScale
from drevo.models.relation import Relation
from drevo.models.relation_grade import RelationGrade
from drevo.models.relation_grade_scale import RelationGradeScale

csrf_protected_method = method_decorator(csrf_protect)


def validate_parameter_int(param, default: int = 0, good_values: list = None):
    """ Валидация параметра param, который может быть числом, строкой или None
        Если передан список good_values - проверяется на вхождение в него
        Если параметр равен None - возвращается default
        Если параметр строка не является числом - возвращается default
        Если параметр не входит в список good_values - возвращается default
    """
    if param is None:
        return default

    if isinstance(param, str):
        if param.isnumeric():
            param = int(param)
        else:
            return default

    if good_values and param not in good_values:
        return default

    return param


class KnowledgeGraderService:
    """Класс для вычисления оценки знания для пользователя user"""
    DEFAULT_KNOWLEDGE_GRADE = 1
    DEFAULT_RELATION_GRADE = 1

    def __init__(self, user, knowledge):
        self.user = user
        self.knowledge = knowledge
        # кэширование справочников в словари
        knowledge_scales = KnowledgeGradeScale.get_cache()
        relation_scales = RelationGradeScale.get_cache()
        self.knowledge_grade_dict = {knowledge.id: knowledge.get_base_grade() for knowledge in knowledge_scales}
        self.relation_grade_dict = {relation.id: relation.get_base_grade() for relation in relation_scales}

    def get_deep_proof_grade(self, knowledge_id):
        """Высчитывает оценку знания по дереву связей"""

        user_relation_grade = RelationGrade.objects.filter(user=self.user, relation=OuterRef('id')).values('grade')
        user_knowledge_grade = KnowledgeGrade.objects.filter(user=self.user, knowledge=OuterRef('rz__id')).values(
            'grade')

        proofs = Relation.objects.filter(
            bz_id=knowledge_id,
            tr__is_argument=True,
            rz__tz__can_be_rated=True,
        ).annotate(
            user_knowledge_grade=Subquery(user_knowledge_grade),
            user_relation_grade=Subquery(user_relation_grade),
            argument_type=F('tr__argument_type'),
        )

        # если потомков нет
        if not proofs:
            return self.DEFAULT_KNOWLEDGE_GRADE

        score = []
        for proof in proofs:
            # оценка связи - пользовательская если есть, иначе по умолчанию
            relation_grade_value = self.relation_grade_dict[
                proof.user_relation_grade] if proof.user_relation_grade else self.DEFAULT_RELATION_GRADE

            # оценка знания - пользовательская если есть, иначе идем вглубь по дереву связей
            if proof.user_knowledge_grade:
                knowledge_grade_value = self.knowledge_grade_dict[proof.user_knowledge_grade]
            else:
                knowledge_grade_value = self.get_deep_proof_grade(proof.rz_id)

            argument_grade_value = knowledge_grade_value * relation_grade_value

            # учитываем в общей оценке только аргументы с положительной оценкой
            # другие аргументы отбрасываются
            if argument_grade_value > 0:
                # знак связи - если "За", то +
                sign = +1 if proof.argument_type == Tr.FOR else -1
                score.append(sign * argument_grade_value)

        result = sum(score) / len(score) if score else 0
        return result

    def calc_proof_grade(self, proof_list, variant: int = 1):
        """ Вычисляет оценку знания и дополняет таблицу доказательной базы proof_list.
            Отличается от get_deep_proof_grade тем, что учитывает варианты оценки и меняет таблицу proof_list
        """
        score = []
        if not proof_list:
            return self.DEFAULT_KNOWLEDGE_GRADE

        for proof in proof_list:
            knowledge_grade_value = proof['user_knowledge_grade_value']
            relation_grade_value = proof['user_relation_grade_value']

            # если нет оценки пользователя, то оценка 1 если вариант 1,
            # в противном случае считаем оценку вглубь
            if knowledge_grade_value is None:
                if variant == 1:
                    common_grade_value = self.DEFAULT_KNOWLEDGE_GRADE
                elif proof['has_children']:
                    common_grade_value = self.get_deep_proof_grade(proof['knowledge_id'])
                else:
                    common_grade_value = self.DEFAULT_KNOWLEDGE_GRADE
            else:
                common_grade_value = knowledge_grade_value

            argument_grade_value = common_grade_value * relation_grade_value
            common_grade = KnowledgeGradeScale.get_grade_object(common_grade_value, use_cache=True)
            argument_grade = KnowledgeGradeScale.get_grade_object(argument_grade_value, use_cache=True)

            if argument_grade_value > 0:
                if proof['relation_type']:
                    score.append(argument_grade_value)
                else:
                    score.append(-argument_grade_value)

            data = {
                'common_grade_id': common_grade.id,  # итоговая оценка знания
                'common_grade_value': common_grade_value,
                'common_grade_text': common_grade.name,

                'argument_grade_id': argument_grade.id,  # оценка довода
                'argument_grade_value': argument_grade_value,  # оценка довода
                'argument_grade_text': argument_grade.name,  # текст оценки
            }
            proof.update(data)

        return sum(score) / len(score) if score else 0

    def get_proof_table(self, knowledge):
        # высчитывает таблицу на основе связей для показа в таблице

        user_relation_grade = RelationGrade.objects.filter(user=self.user, relation=OuterRef('id')).values('grade')
        user_knowledge_grade = KnowledgeGrade.objects.filter(user=self.user, knowledge=OuterRef('rz__id')).values(
            'grade')
        has_children = Relation.objects.filter(bz=OuterRef('rz'), tr__is_argument=True, rz__tz__can_be_rated=True)

        relations = knowledge.base.filter(
            Q(tr__is_argument=True),
            Q(rz__tz__can_be_rated=True),
        ).order_by("tr__name").annotate(
            user_knowledge_grade=Subquery(user_knowledge_grade),
            user_relation_grade=Subquery(user_relation_grade),
            has_children=Exists(has_children),
            argument_type=F('tr__argument_type'),
            argument_name=F('tr__name'),
            knowledge_id=F('rz__id'),
            knowledge_name=F('rz__name')
        )

        proof_relations = []

        for relation in relations:
            knowledge_grade_id = relation.user_knowledge_grade
            knowledge_grade_value = self.knowledge_grade_dict.get(knowledge_grade_id, None)
            relation_grade_id = relation.user_relation_grade
            relation_grade_value = self.relation_grade_dict.get(relation_grade_id, 1)

            data = {'knowledge_id': relation.knowledge_id,
                    'knowledge_name': relation.knowledge_name,
                    'has_children': relation.has_children,

                    'relation_id': relation.id,
                    'relation_name': relation.argument_name,
                    'relation_type': relation.argument_type == Tr.FOR,

                    'user_knowledge_grade_value': knowledge_grade_value,
                    'user_knowledge_grade_id': knowledge_grade_id,

                    'user_relation_grade_value': relation_grade_value,
                    'user_relation_grade_id': relation_grade_id,
                    }

            proof_relations.append(data)

        return proof_relations

    def get_grades(self, proof_base_value):
        proof_grade = KnowledgeGradeScale.get_grade_object(proof_base_value, use_cache=True)

        user_knowledge_grade = KnowledgeGrade.objects.filter(user=self.user,
                                                             knowledge=self.knowledge).select_related('grade').first()

        if user_knowledge_grade:
            user_knowledge_grade_id = user_knowledge_grade.grade.id
            user_knowledge_grade_value = user_knowledge_grade.grade.get_base_grade()

        else:
            user_knowledge_grade_id = KnowledgeGradeScale.get_default_grade().id
            user_knowledge_grade_value = None

        common_grade_value = user_knowledge_grade_value if user_knowledge_grade else proof_base_value
        common_grade = KnowledgeGradeScale.get_grade_object(common_grade_value, use_cache=True)

        return {
            'proof_grade_id': proof_grade.id,
            'proof_grade_value': proof_base_value,
            'proof_grade_text': proof_grade.name,

            'user_knowledge_grade_id': user_knowledge_grade_id,
            'user_knowledge_grade_value': user_knowledge_grade_value,

            'common_grade_id': common_grade.id,
            'common_grade_value': common_grade_value,
            'common_grade_text': common_grade.name,
        }


class KnowledgeFormView(LoginRequiredMixin, TemplateView):
    template_name = "drevo/knowledge_grade.html"

    def get_context_data(self, **kwargs):
        user = self.request.user
        knowledge = get_object_or_404(Znanie.objects.select_related('tz'), id=kwargs.get("pk"))
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

        variant = validate_parameter_int(self.request.GET.get("variant"), default=1, good_values=[1, 2])
        context["variant"] = variant

        grader = KnowledgeGraderService(user, knowledge)
        proof_relations = grader.get_proof_table(knowledge)
        context["proof_relations"] = proof_relations

        proof_base_value = grader.calc_proof_grade(proof_relations, variant=variant)
        grades = grader.get_grades(proof_base_value)
        context.update(grades)

        return context

    def post(self, request, *args, **kwargs):
        user = request.user
        knowledge_pk = kwargs.get("pk")
        data = json.loads(request.POST.get('data'))

        new_knowledge_grade = data.get('new_knowledge_grade', None)
        new_relation_grade = data.get('new_relation_grade', None)
        proof_relation = data.get('relation', None)
        proof_knowledge = data.get('knowledge', None)

        if (new_knowledge_grade and
                proof_knowledge and
                new_knowledge_grade != KnowledgeGradeScale.get_default_grade().id):
            KnowledgeGrade.objects.update_or_create(
                knowledge_id=proof_knowledge,
                user=user,
                defaults={"grade_id": new_knowledge_grade},
            )

        if (new_relation_grade and
                proof_relation and
                new_relation_grade != RelationGradeScale.get_default_grade().id):
            RelationGrade.objects.update_or_create(
                relation_id=proof_relation,
                user=user,
                defaults={"grade_id": new_relation_grade},
            )

        return self.get(request, *args, **kwargs)
        #return HttpResponseRedirect(self.request.path)


class KnowledgeFormView2(TemplateView):
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
        context["variant"] = variant

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
