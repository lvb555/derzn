import logging

from django.db.models import Exists, F, OuterRef, Q, Subquery

from drevo.models import Relation, Tr
from drevo.models.knowledge_grade import KnowledgeGrade
from drevo.models.knowledge_grade_scale import KnowledgeGradeScale
from drevo.models.relation_grade import RelationGrade
from drevo.models.relation_grade_scale import RelationGradeScale

logger = logging.getLogger(__name__)


class KnowledgeGraderService:
    """Класс для вычисления оценки знания для пользователя user
    использование:
    grader = KnowledgeGraderService(user, knowledge)

    proof_relations = grader.get_proof_table(knowledge)
    proof_base_value = grader.calc_proof_grade(proof_relations, variant=variant)
    grades = grader.get_grades(proof_base_value)
    или
    proof_relations, grades = grader.do_calc(variant=variant)

    """

    DEFAULT_KNOWLEDGE_GRADE_VALUE = 1
    DEFAULT_RELATION_GRADE_VALUE = 1

    def __init__(self, user, knowledge):
        self.user = user
        self.knowledge = knowledge
        # кэширование справочников в словари
        knowledge_scales = KnowledgeGradeScale.get_cache()
        relation_scales = RelationGradeScale.get_cache()
        self.knowledge_grade_dict = {
            knowledge.id: knowledge.get_base_grade() for knowledge in knowledge_scales
        }
        self.relation_grade_dict = {
            relation.id: relation.get_base_grade() for relation in relation_scales
        }

    def get_deep_proof_grade(self, knowledge_id, visited=None):
        """Высчитывает оценку знания по дереву связей - вызывает рекурсивно"""

        # для предотвращения циклов при вычислении
        if visited is None:
            visited = set()

        elif knowledge_id in visited:
            # это цикл!!!
            logger.warning(f"Обнаружен цикл в аргументах знания [{self.knowledge}]")
            return 0

        visited.add(knowledge_id)

        user_relation_grade = RelationGrade.objects.filter(
            user=self.user, relation=OuterRef("id")
        ).values("grade")
        user_knowledge_grade = KnowledgeGrade.objects.filter(
            user=self.user, knowledge=OuterRef("rz__id")
        ).values("grade")

        proofs = Relation.objects.filter(
            bz_id=knowledge_id,
            tr__is_argument=True,
            rz__tz__can_be_rated=True,
        ).annotate(
            user_knowledge_grade=Subquery(user_knowledge_grade),
            user_relation_grade=Subquery(user_relation_grade),
            argument_type=F("tr__argument_type"),
        )

        # если потомков нет
        if not proofs:
            return self.DEFAULT_KNOWLEDGE_GRADE_VALUE

        score = []
        for proof in proofs:
            # оценка связи - пользовательская если есть, иначе по умолчанию
            relation_grade_value = (
                self.relation_grade_dict[proof.user_relation_grade]
                if proof.user_relation_grade
                else self.DEFAULT_RELATION_GRADE_VALUE
            )

            # оценка знания - пользовательская если есть, иначе идем вглубь по дереву связей
            if proof.user_knowledge_grade:
                knowledge_grade_value = self.knowledge_grade_dict[
                    proof.user_knowledge_grade
                ]
            else:
                knowledge_grade_value = self.get_deep_proof_grade(proof.rz_id, visited)

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
        """Вычисляет оценку знания и дополняет таблицу доказательной базы proof_list.
        Отличается от get_deep_proof_grade тем, что учитывает варианты оценки и
        меняет таблицу proof_list, добавляя оценки
        """
        score = []
        if not proof_list:
            return self.DEFAULT_KNOWLEDGE_GRADE_VALUE

        for proof in proof_list:
            knowledge_grade_value = proof["user_knowledge_grade_value"]
            relation_grade_value = proof["user_relation_grade_value"]

            # если нет оценки пользователя или оценка пользователя равна 0, то оценка 1 если вариант 1,
            # в противном случае считаем оценку вглубь
            if not knowledge_grade_value:
                if variant == 1:
                    common_grade_value = self.DEFAULT_KNOWLEDGE_GRADE_VALUE
                elif proof["has_children"]:
                    common_grade_value = self.get_deep_proof_grade(
                        proof["knowledge_id"]
                    )
                else:
                    common_grade_value = self.DEFAULT_KNOWLEDGE_GRADE_VALUE
            else:
                common_grade_value = knowledge_grade_value

            argument_grade_value = common_grade_value * relation_grade_value
            common_grade = KnowledgeGradeScale.get_grade_object(
                common_grade_value, use_cache=True
            )
            argument_grade = KnowledgeGradeScale.get_grade_object(
                argument_grade_value, use_cache=True
            )

            if argument_grade_value > 0:
                if proof["relation_type"]:
                    score.append(argument_grade_value)
                else:
                    score.append(-argument_grade_value)

            data = {
                "common_grade_id": common_grade.id,  # итоговая оценка знания
                "common_grade_value": common_grade_value,
                "common_grade_text": common_grade.name,
                "argument_grade_id": argument_grade.id,  # оценка довода
                "argument_grade_value": argument_grade_value,  # оценка довода
                "argument_grade_text": argument_grade.name,  # текст оценки
            }
            proof.update(data)

        return sum(score) / len(score) if score else 0

    def get_proof_table(self):
        # высчитывает таблицу на основе связей для показа в таблице

        user_relation_grade = RelationGrade.objects.filter(
            user=self.user, relation=OuterRef("id")
        ).values("grade")
        user_knowledge_grade = KnowledgeGrade.objects.filter(
            user=self.user, knowledge=OuterRef("rz__id")
        ).values("grade")
        has_children = Relation.objects.filter(
            bz=OuterRef("rz"), tr__is_argument=True, rz__tz__can_be_rated=True
        )

        relations = (
            self.knowledge.base.filter(
                Q(tr__is_argument=True),
                Q(rz__tz__can_be_rated=True),
            )
            .order_by("tr__name")
            .annotate(
                user_knowledge_grade=Subquery(user_knowledge_grade),
                user_relation_grade=Subquery(user_relation_grade),
                has_children=Exists(has_children),
                argument_type=F("tr__argument_type"),
                argument_name=F("tr__name"),
                knowledge_id=F("rz__id"),
                knowledge_name=F("rz__name"),
            )
        )

        proof_relations = []

        for relation in relations:
            knowledge_grade_id = relation.user_knowledge_grade
            knowledge_grade_value = self.knowledge_grade_dict.get(
                knowledge_grade_id, None
            )
            relation_grade_id = relation.user_relation_grade
            relation_grade_value = self.relation_grade_dict.get(relation_grade_id, 1)

            data = {
                "knowledge_id": relation.knowledge_id,
                "knowledge_name": relation.knowledge_name,
                "has_children": relation.has_children,
                "relation_id": relation.id,
                "relation_name": relation.argument_name,
                "relation_type": relation.argument_type == Tr.FOR,
                "user_knowledge_grade_value": knowledge_grade_value,
                "user_knowledge_grade_id": knowledge_grade_id,
                "user_relation_grade_value": relation_grade_value,
                "user_relation_grade_id": relation_grade_id,
            }

            proof_relations.append(data)

        return proof_relations

    def get_grades(self, proof_base_value) -> dict:
        """
        Вспомогательный метод
        Высчитывает оценки знания исходя из оценки доказательной базы proof_base_value и оценки пользователя
        Возвращает словарь с оценками:
            id - идентификатор оценки
            value - значение оценки
            text - текст оценки
        """
        proof_grade = KnowledgeGradeScale.get_grade_object(
            proof_base_value, use_cache=True
        )

        user_knowledge_grade = (
            KnowledgeGrade.objects.filter(user=self.user, knowledge=self.knowledge)
            .select_related("grade")
            .first()
        )

        if user_knowledge_grade:
            user_knowledge_grade_id = user_knowledge_grade.grade.id
            user_knowledge_grade_value = user_knowledge_grade.grade.get_base_grade()

        else:
            user_knowledge_grade_id = KnowledgeGradeScale.get_default_grade().id
            user_knowledge_grade_value = None

        common_grade_value = (
            user_knowledge_grade_value
            if user_knowledge_grade_value
            else proof_base_value
        )
        common_grade = KnowledgeGradeScale.get_grade_object(
            common_grade_value, use_cache=True
        )

        return {
            "proof_grade_id": proof_grade.id,
            "proof_grade_value": proof_base_value,
            "proof_grade_text": proof_grade.name,
            "user_knowledge_grade_id": user_knowledge_grade_id,
            "user_knowledge_grade_value": user_knowledge_grade_value,
            "common_grade_id": common_grade.id,
            "common_grade_value": common_grade_value,
            "common_grade_text": common_grade.name,
        }

    def do_calc(self, variant) -> tuple[list[dict], dict]:
        """Делает всю работу, возвращает список для таблицы и словарь с оценками"""
        proof_relations = self.get_proof_table()
        proof_base_value = self.calc_proof_grade(proof_relations, variant=variant)
        grades = self.get_grades(proof_base_value)

        return proof_relations, grades
