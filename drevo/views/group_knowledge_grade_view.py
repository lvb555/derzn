import datetime
import copy

from statistics import mean
from dataclasses import dataclass
from django.views.generic import TemplateView
from django.db.models import F
from drevo.models.knowledge_grade import KnowledgeGrade
from drevo.models.knowledge_grade_scale import KnowledgeGradeScale
from drevo.models.knowledge import Znanie
from drevo.models.relation import Relation
from drevo.models.relation_grade import RelationGrade
from drevo.models.relation_grade_scale import RelationGradeScale
from django.shortcuts import Http404, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from users.models import User, Profile

csrf_protected_method = method_decorator(csrf_protect)

@dataclass
class Grade:
    name: str | None = None
    value: float = 0.0

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

            self.get_group_users()
            base_grade, proof_base_grade, common_grade = \
                    self.get_average_base_grade(knowledge)

            context['base_grade'] = base_grade
            context['knowledge'] = knowledge

            proof_relations = knowledge.base.filter(
                tr__is_argument=True,
                rz__tz__can_be_rated=True,
            )

            context['proof_relations'] = self.get_group_relations(proof_relations)

            context['proof_base_grade'] = proof_base_grade
            context['common_grade'] = common_grade
        return context

    @staticmethod
    def get_name_knowledge_grade_scale(value: float) -> str:
        """
        Получение название шкалы оценки знания по значению оценки знания

        - value - значение оценки знания
        - возвращается название шкалы оценки знания
        """
        return KnowledgeGradeScale.get_grade_object(value).name

    @staticmethod
    def get_name_relation_grade_scale(value: float) -> str:
        """
        Получение название шкалы оценки связи по значению оценки связи

        - value - значение оценки связи
        - возвращается название шкалы оценки связи
        """
        return RelationGradeScale.get_grade_object(value).name

    def get_grade_from_knowledge_value(self, value: float) -> Grade:
        """
        Получение объекта Grade из значения оценки знания

        - value - значение оценки знания
        - возвращается объект Grade
        """
        grade = Grade(
            name = self.get_name_knowledge_grade_scale(value),
            value = value
        )
        return grade

    def get_grade_from_relation_value(self, value: float) -> Grade:
        """
        Получение объекта Grade из значения оценки связи

        - value - значение оценки связи
        - возвращается объект Grade
        """
        grade = Grade(
            name = self.get_name_relation_grade_scale(value),
            value = value
        )
        return grade

    def get_average_base_grade(self, knowledge: Znanie) -> tuple[Grade, Grade, Grade]:
        """
        Получение среднего значения, по всей группе пользователей, оценки
        знания (base_grade), оценки доказательной базы (proof_base_grade),
        общей оценки знания (common_grade)

        - knowledge - знание, для которого мы находим среднее значение оценок
        - возвращается кортеж из следующих оценок:
            base_grade (средняя оценка знания),
            proof_base_grade (средняя оценка доказательной базы),
            common_grade (средняя общая оценка знания)
        """
        users = self.users
        copy_request = copy.copy(self.request)

        grades = {
            "base_grade": Grade(),
            "proof_base_grade": Grade(),
            "common_grade": Grade()
        }
        counts_grade = {
            "base_grade": 0.01,
            "proof_base_grade": 0.01,
            "common_grade": 0.01
        }

        # цикл в котором для каждого пользователя вычисляются и сохраняются
        # оценки знания, доказательной базы, общей оценки знания
        for user in users:
            copy_request.user = user
            base_knowledge_grade = KnowledgeGrade.objects.filter(
                knowledge=knowledge,
                user=user,
            ).first()
            if base_knowledge_grade:
                base_grade_value = base_knowledge_grade.grade.get_base_grade()
                if base_grade_value:
                    counts_grade["base_grade"] += 1
                    grades["base_grade"].value += base_grade_value

            common_grade_value, proof_base_value = knowledge.get_common_grades(
                request=copy_request)
            if proof_base_value:
                counts_grade["proof_base_grade"] += 1
                grades["proof_base_grade"].value += proof_base_value
            if common_grade_value:
                counts_grade["common_grade"] += 1
                grades["common_grade"].value += common_grade_value

        # цикл в котором для каждой оценки вычисляется среднее значение и
        # сохраняется
        for label in grades:
            grades[label].value = grades[label].value / counts_grade[label]
            grades[label].name = self.get_name_knowledge_grade_scale(grades[label].value)
        return grades["base_grade"], grades["proof_base_grade"], grades["common_grade"]

    def get_group_users(self) -> None:
        """
        Функция для получения группы пользователей
        Группы пользователей сохраняются в self.users
        """
        gender = self.request.GET.get("gender", None)
        age_from_to = {
            "min_age": int(self.request.GET.get("min_age", 0)),
            "max_age": int(self.request.GET.get("max_age", 0)),
        }

        profiles = None
        if gender:
            # получение всех профилей определенного пола
            profiles = Profile.objects.prefetch_related('user').filter(
                gender=gender
            )
        if age_from_to["max_age"] > 0:
            if profiles is None:
                # получение всех профилей, которые оценивали знание
                profiles = Profile.objects.filter(user__id__in=set(map(
                    lambda x: x.user.id,
                    KnowledgeGrade.objects.prefetch_related("user").filter(
                        knowledge__id=self.knowledge_id))))
            # получение всех профилей, удовлятворяющих интервалу возраста
            now = datetime.date.today()
            min_age, max_age = datetime.timedelta(days=365*age_from_to["min_age"]),\
                               datetime.timedelta(days=365*age_from_to["max_age"])
            profiles = profiles.exclude(birthday_at=None)\
                                 .annotate(age=(now - F("birthday_at")))\
                                 .filter(age__gte=min_age, age__lt=max_age)
        if profiles is None:
            # получение всех пользователей, которые оценивали знание
            self.users = User.objects.filter(id__in=set(map(
                lambda x: x.user.id,
                KnowledgeGrade.objects.prefetch_related("user").filter(
                    knowledge__id=self.knowledge_id))))
            return
        self.users = list(map(lambda x: x.user, profiles))

    def get_grade_values(self, relation: Relation) -> dict:
        """
        Получение все значения, по всей группе пользователей, оценки довода
        (proof_grade), общей оценки (common_grade), оценки знания
        (knowledge_grade), оценки связи (relation_grade)

        - relation - связь
        - возвращается словарь, следующей структуры:
        {
            "proof_grade" (значения оценки довода),
            "common_grade" (значения общей оценки),
            "knowledge_grade" (значения оценки знания),
            "relation_grade" (значения оценки связи)
        }
        """
        users = self.users
        copy_request = copy.copy(self.request)
        grade_values = {
            "proof_grade": [],
            "common_grade": [],
            "knowledge_grade": [],
            "relation_grade": []
        }
        for user in users:
            copy_request.user = user

            # добавление значения оценки довода в список
            proof_grade = relation.get_proof_weight(
                copy_request,
                copy_request.GET.get("variant", 2)
            )
            if proof_grade:
                grade_values["proof_grade"].append(proof_grade)

            # добавление значения общей оценки знания в список
            common_grade, _ = relation.rz.get_common_grades(
                request=copy_request)
            if common_grade:
                grade_values["common_grade"].append(common_grade)

            # добавление значения оценки знания в список
            knowledge_grade = KnowledgeGrade.objects.filter(
                knowledge=relation.rz,
                user=user
            ).first()
            if knowledge_grade:
                knowledge_grade_value = knowledge_grade.grade.get_base_grade()
                if knowledge_grade_value:
                    grade_values["knowledge_grade"].append(
                        knowledge_grade_value
                    )

            # добавление значения оценки связи в список
            relation_grade = RelationGrade.objects.filter(
                relation=relation,
                user=user
            ).first()
            if relation_grade:
                relation_grade_value = relation_grade.grade.get_base_grade()
                if relation_grade_value:
                    grade_values["relation_grade"].append(
                        relation_grade_value
                    )
        return grade_values

    def get_average_grades(self, relation: Relation) -> dict:
        """
        Вычисление средних значений оценок для связи

        - relation - связь
        - возвращается словарь, следующей структуры:
        {
            "proof_grade" (среднее значение оценки довода),
            "common_grade" (среднее значение общей оценки),
            "knowledge_grade" (среднее значение оценки знания),
            "relation_grade" (среднее значение оценки связи)
        }

        """
        grade_values = self.get_grade_values(relation)
        for label in grade_values:
            grade_values[label] = mean(grade_values[label]) \
                                  if len(grade_values[label]) >= 1 \
                                  else 0

        grades = {
            "proof_grade": self.get_grade_from_knowledge_value(
                grade_values["proof_grade"]),
            "common_grade": self.get_grade_from_knowledge_value(
                grade_values["common_grade"]),
            "knowledge_grade": self.get_grade_from_knowledge_value(
                grade_values["knowledge_grade"]),
            "relation_grade": self.get_grade_from_relation_value(
                grade_values["relation_grade"]),
        }
        return grades

    def get_group_relations(self, relations: list[Relation]) -> list[dict]:
        """
        Получение для всех связей - средних значений оценок связи и других
        данных о связи

        - relations - список связей со знанием
        - возвращается список из словарей следующей структуры:
        [
            {
                "knowledge_url" - ссылка до связанного знания
                "knowledge_name" - имя связанного знания
                "type_name" - тип связи
                "proof_grade" - среднее значение оценки довода для группы
                                пользователей
                "common_grade" - среднее значение общей оценки знания для
                                 группы пользователей
                "knowledge_grade" - среднее значение оценки знания для группы
                                    пользователей
                "grade" - среднее значение оценки связи для группы
                          пользователей
            },
            ...
        ]
        """
        group_relations = []
        for relation in relations:
            if relation.tr.is_argument:
                grades = self.get_average_grades(relation)
                group_relations.append({
                    "knowledge_url": relation.rz.get_absolute_url(),
                    "knowledge_name": relation.rz.name,
                    "type_name": relation.tr.name,
                    "proof_grade": grades["proof_grade"],
                    "common_grade": grades["common_grade"],
                    "knowledge_grade": grades["knowledge_grade"],
                    "grade": grades["relation_grade"],
                })
        return group_relations
