import logging
from typing import Callable

from django.db.models import Exists, F, OuterRef, Q, Subquery

from drevo.models import Relation, Tr, Znanie
from drevo.models.knowledge_grade import KnowledgeGrade
from drevo.models.knowledge_grade_scale import KnowledgeGradeScale
from drevo.models.relation_grade import RelationGrade
from drevo.models.relation_grade_scale import RelationGradeScale

logger = logging.getLogger(__name__)


class ProofScore:
    """Вспомогательный класс для вычисления оценки доказательной базы"""

    def __init__(self):
        self.score = []

    def add(self, is_argument: bool, value: float):
        if value > 0:
            if is_argument:
                self.score.append(value)
            else:
                self.score.append(-value)

    def mean(self) -> float:
        return sum(self.score) / len(self.score) if self.score else 0


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

    DEFAULT_KNOWLEDGE_GRADE_VALUE = 1.0
    DEFAULT_RELATION_GRADE_VALUE = 1.0

    def __init__(self, user, knowledge):
        self.user = user
        self.knowledge = knowledge
        # кэширование справочников в словари
        knowledge_scales = KnowledgeGradeScale.get_cache()
        relation_scales = RelationGradeScale.get_cache()
        self.knowledge_grade_dict = {knowledge.id: knowledge for knowledge in knowledge_scales}
        self.relation_grade_dict = {relation.id: relation for relation in relation_scales}

    def get_deep_proof_grade(self, knowledge_id, visited=None) -> float:
        """Высчитывает оценку знания по дереву связей - вызывает рекурсивно"""

        # для предотвращения циклов при вычислении
        if visited is None:
            visited = set()

        elif knowledge_id in visited:
            # это цикл!!!
            logger.warning(f"Обнаружен цикл в аргументах знания [{self.knowledge}]")
            return 0

        visited.add(knowledge_id)

        user_relation_grade = RelationGrade.objects.filter(user=self.user, relation=OuterRef("id")).values("grade")
        user_knowledge_grade = KnowledgeGrade.objects.filter(user=self.user, knowledge=OuterRef("rz__id")).values(
            "grade"
        )

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

        score = ProofScore()
        for proof in proofs:
            # оценка связи - пользовательская если есть, иначе по умолчанию
            _, relation_grade_value = self._get_relation_grade_by_id(proof.user_relation_grade)

            # оценка знания - пользовательская если есть, иначе идем вглубь по дереву связей
            _, knowledge_grade_value = self._get_knowledge_grade_by_id(proof.user_knowledge_grade)

            if knowledge_grade_value == 0:
                knowledge_grade_value = self.get_deep_proof_grade(proof.rz_id, visited)

            argument_grade_value = knowledge_grade_value * relation_grade_value
            score.add(proof.argument_type == Tr.FOR, argument_grade_value)

        return score.mean()

    def calc_proof_grade(self, proof_list, variant: int = 1):
        """Вычисляет оценку знания и дополняет таблицу доказательной базы proof_list.
        Отличается от get_deep_proof_grade тем, что учитывает варианты оценки и
        меняет таблицу proof_list, добавляя оценки
        """
        if not proof_list:
            return self.DEFAULT_KNOWLEDGE_GRADE_VALUE

        score = ProofScore()

        for proof in proof_list:
            knowledge_grade_value = proof["user_knowledge_grade_value"]
            relation_grade_value = proof["user_relation_grade_value"]

            if proof["has_children"]:
                common_grade_value = self._get_common_grade_value(
                    user_grade_value=knowledge_grade_value,
                    proof_base_value=lambda: self.get_deep_proof_grade(proof["knowledge_id"]),
                    variant=variant)

            else:
                # нет потомков - не идем вглубь
                common_grade_value = self._get_common_grade_value(
                    user_grade_value=knowledge_grade_value,
                    proof_base_value=None,
                    variant=variant)

            argument_grade_value = common_grade_value * relation_grade_value
            common_grade = KnowledgeGradeScale.get_grade_object(common_grade_value, use_cache=True)
            argument_grade = KnowledgeGradeScale.get_grade_object(argument_grade_value, use_cache=True)
            score.add(proof["relation_type"], argument_grade_value)

            data = {
                "common_grade_id": common_grade.pk,  # итоговая оценка знания
                "common_grade_value": common_grade_value,
                "common_grade_text": common_grade.name,
                "argument_grade_id": argument_grade.pk,  # оценка довода
                "argument_grade_value": argument_grade_value,  # оценка довода
                "argument_grade_text": argument_grade.name,  # текст оценки
            }
            proof.update(data)

        return score.mean()

    def get_proof_table(self, knowledge_id: Znanie = None) -> list[dict]:
        # высчитывает таблицу на основе связей для показа в таблице
        if not knowledge_id:
            knowledge_id = self.knowledge.pk

        user_relation_grade = RelationGrade.objects.filter(user=self.user, relation=OuterRef("id")).values("grade")
        user_knowledge_grade = KnowledgeGrade.objects.filter(user=self.user, knowledge=OuterRef("rz__id")).values(
            "grade"
        )
        has_children = Relation.objects.filter(bz=OuterRef("rz"), tr__is_argument=True, rz__tz__can_be_rated=True)

        relations = (
            Relation.objects.filter(
                Q(bz=knowledge_id),
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
            user_knowledge_grade, knowledge_grade_value = self._get_knowledge_grade_by_id(relation.user_knowledge_grade)
            knowledge_grade_id = user_knowledge_grade.pk

            relation_grade, relation_grade_value = self._get_relation_grade_by_id(relation.user_relation_grade)
            relation_grade_id = relation_grade.pk

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

    def _get_knowledge_grade_by_id(self, knowledge_grade_id: int | None) -> tuple[KnowledgeGradeScale, float]:
        """По id возвращает оценку знания и ее значение,
        если id None, то возвращает оценку по умолчанию и None (чтобы не отображалось значение)"""
        if knowledge_grade_id:
            knowledge_grade = self.knowledge_grade_dict[knowledge_grade_id]
            value = knowledge_grade.get_base_grade()
        else:
            knowledge_grade = KnowledgeGradeScale.get_default_grade()
            value = None

        return knowledge_grade, value

    def _get_relation_grade_by_id(self, relation_grade_id: int | None) -> tuple[RelationGradeScale, float]:
        """По id возвращает оценку знания и ее значение,
           если id None, то возвращает оценку и значение по умолчанию"""
        if relation_grade_id:
            relation_grade = self.relation_grade_dict[relation_grade_id]
            value = relation_grade.get_base_grade()
        else:
            relation_grade = KnowledgeGradeScale.get_default_grade()
            value = self.DEFAULT_RELATION_GRADE_VALUE

        return relation_grade, value

    def _get_user_grade(self, knowledge: Znanie) -> tuple[KnowledgeGradeScale, float | None]:
        """Возвращает оценку пользователя для знания и ее значение, если она есть
        Иначе возвращает оценку по умолчанию и значение None
        """
        user_knowledge_grade = (
            KnowledgeGrade.objects.filter(user=self.user, knowledge=knowledge).values("grade").first()
        )
        #
        user_knowledge_grade_id = user_knowledge_grade['grade'] if user_knowledge_grade else None
        user_knowledge_grade, user_knowledge_grade_value = self._get_knowledge_grade_by_id(user_knowledge_grade_id)

        return user_knowledge_grade, user_knowledge_grade_value

    def _get_common_grade_value(self, user_grade_value: float | None,
                                proof_base_value: float | Callable | None, variant: int) -> float:
        """Метод высчитывает общую оценку знания"""
        # если есть оценка пользователя не 0, то возвращаем ее
        if user_grade_value:
            return user_grade_value

        # если вариант 1, возвращаем оценку по умолчанию
        if variant == 1 or proof_base_value is None:
            common_grade_value = self.DEFAULT_KNOWLEDGE_GRADE_VALUE
        else:
            # если вариант 2 ....
            # если функция - вызываем ее
            if callable(proof_base_value):
                common_grade_value = proof_base_value()
            else:
                common_grade_value = proof_base_value

        return common_grade_value

    def get_grades(self, proof_base_value) -> dict:
        """
        Вспомогательный метод.
        Высчитывает оценки знания исходя из оценки доказательной базы proof_base_value и оценки пользователя.
        Возвращает словарь с оценками:
            id - идентификатор оценки
            value - значение оценки
            text - текст оценки
        """
        proof_grade = KnowledgeGradeScale.get_grade_object(proof_base_value, use_cache=True)

        user_knowledge_grade, user_knowledge_grade_value = self._get_user_grade(self.knowledge)

        # высчитывает общую оценку по варианту 2 - учитываем доказательную базу
        common_grade_value = self._get_common_grade_value(user_knowledge_grade_value, proof_base_value, variant=2)
        common_grade = KnowledgeGradeScale.get_grade_object(common_grade_value, use_cache=True)

        return {
            "proof_grade_id": proof_grade.pk,
            "proof_grade_value": proof_base_value,
            "proof_grade_text": proof_grade.name,
            "user_knowledge_grade_id": user_knowledge_grade.pk,
            "user_knowledge_grade_value": user_knowledge_grade_value,
            "user_knowledge_grade_text": user_knowledge_grade.name,
            "common_grade_id": common_grade.pk,
            "common_grade_value": common_grade_value,
            "common_grade_text": common_grade.name,
        }

    def do_calc(self, variant) -> tuple[list[dict], dict]:
        """Делает всю работу, возвращает список для таблицы и словарь с оценками"""
        proof_relations = self.get_proof_table()
        proof_base_value = self.calc_proof_grade(proof_relations, variant=variant)
        grades = self.get_grades(proof_base_value)

        return proof_relations, grades

    """ Функции для получения дерева оценок для знания
        Дерево представляет собой словарь, потомки хранятся в списке по ключу 'proof_relations'
        корень дерева - основное знание self.knowledge
        Основное использование - get_tree(variant)
        build_tree() и calc_tree() - вспомогательные методы
    """

    def build_tree(self) -> dict:
        """Возвращает словарь для дерева"""

        # заполняем дерево
        user_knowledge_grade, user_knowledge_grade_value = self._get_user_grade(self.knowledge)
        # для root надо заполнить данные отдельно

        root = {
            "knowledge_id": self.knowledge.id,
            "user_knowledge_grade_id": user_knowledge_grade.pk,
            "user_knowledge_grade_value": user_knowledge_grade_value,
            "user_knowledge_grade_text": user_knowledge_grade.name,
            "has_children": True,
        }

        queue = [root]
        visited = set()  # для учета повторов
        while queue:
            knowledge = queue.pop(0)

            # проверяем на цикл
            knowledge_id = knowledge["knowledge_id"]
            if knowledge_id in visited:
                logger.warning(f"Обнаружен цикл - знание id: {knowledge_id}")
                continue

            visited.add(knowledge_id)
            if knowledge["has_children"]:
                proof_relations = self.get_proof_table(knowledge_id=knowledge_id)
                if not proof_relations:
                    knowledge["has_children"] = False
                else:
                    for child in proof_relations:
                        queue.append(child)
            else:
                proof_relations = []
            knowledge["proof_relations"] = proof_relations
        return root

    def _node_grades(self, node: dict, proof_base_value: float, variant: int) -> dict:
        """Функция для вычисления оценки узла дерева
        в зависимости от варианта расчета оценки и оценки доказательной базы
        возвращает словарь с 3мя оценками
        """
        proof_grade = KnowledgeGradeScale.get_grade_object(proof_base_value, use_cache=True)
        user_knowledge_grade_value = node["user_knowledge_grade_value"]
        user_knowledge_grade_id = node["user_knowledge_grade_id"]

        if node["knowledge_id"] == self.knowledge.id:
            # для корневого знания в любом случае надо учесть доказательную базу, поэтому вариант 2
            common_grade_value = self._get_common_grade_value(user_knowledge_grade_value, proof_base_value, 2)
        else:
            common_grade_value = self._get_common_grade_value(user_knowledge_grade_value, proof_base_value, variant)

        common_grade = KnowledgeGradeScale.get_grade_object(common_grade_value, use_cache=True)

        return {
            "proof_grade_id": proof_grade.pk,
            "proof_grade_value": proof_base_value,
            "proof_grade_text": proof_grade.name,
            "user_knowledge_grade_id": user_knowledge_grade_id,
            "user_knowledge_grade_value": user_knowledge_grade_value,
            "user_knowledge_grade_text": self.knowledge_grade_dict[user_knowledge_grade_id].name,
            "common_grade_id": common_grade.pk,
            "common_grade_value": common_grade_value,
            "common_grade_text": common_grade.name,
        }

    def calc_tree(self, root: dict, variant) -> float:
        """Рекурсивная функция для вычисления оценок дерева.
        Возвращает итоговую оценку узла с учетом варианта оценки
        """
        proof_relations = root["proof_relations"]
        if proof_relations:
            score = ProofScore()
            for child in proof_relations:
                # calc_tree надо вызвать в любом случае - обходим дерево
                child_grade_value = self.calc_tree(child, variant)
                child_relation_grade_value = child["user_relation_grade_value"]
                argument_grade_value = child_grade_value * child_relation_grade_value
                score.add(child["relation_type"], argument_grade_value)

            proof_base_value = score.mean()

        else:
            proof_base_value = self.DEFAULT_KNOWLEDGE_GRADE_VALUE

        grades = self._node_grades(root, proof_base_value, variant)
        root.update(grades)
        return grades["common_grade_value"]

    def get_tree(self, variant) -> dict:
        """Возвращает дерево (словарь) с оценками по всему знанию"""
        tree = self.build_tree()
        self.calc_tree(tree, variant)
        return tree
