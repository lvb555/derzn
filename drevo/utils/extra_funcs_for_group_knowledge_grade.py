import datetime
import copy

from statistics import mean
from dataclasses import dataclass
from django.db.models import F
from drevo.models.knowledge import Znanie
from drevo.models.knowledge_grade import KnowledgeGrade
from drevo.models.knowledge_grade_scale import KnowledgeGradeScale
from drevo.models.relation import Relation
from drevo.models.relation_grade import RelationGrade
from drevo.models.relation_grade_scale import RelationGradeScale
from users.models import User, Profile


@dataclass
class Grade:
    name: str | None = None
    value: float = 0.0

def get_name_knowledge_grade_scale(value: float) -> str:
    """
    Получение название шкалы оценки знания по значению оценки знания

    - value - значение оценки знания
    - возвращается название шкалы оценки знания
    """
    return KnowledgeGradeScale.get_grade_object(value).name

def get_name_relation_grade_scale(value: float) -> str:
    """
    Получение название шкалы оценки связи по значению оценки связи

    - value - значение оценки связи
    - возвращается название шкалы оценки связи
    """
    return RelationGradeScale.get_grade_object(value).name

def get_grade_from_knowledge_value(value: float) -> Grade:
    """
    Получение объекта Grade из значения оценки знания

    - value - значение оценки знания
    - возвращается объект Grade
    """
    grade = Grade(
        name = get_name_knowledge_grade_scale(value),
        value = value
    )
    return grade

def get_grade_from_relation_value(value: float) -> Grade:
    """
    Получение объекта Grade из значения оценки связи

    - value - значение оценки связи
    - возвращается объект Grade
    """
    grade = Grade(
        name = get_name_relation_grade_scale(value),
        value = value
    )
    return grade

def get_average_base_grade(users, request , knowledge: Znanie) -> tuple[Grade, Grade, Grade]:
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
    copy_request = copy.copy(request)

    grades = {
        "base_grade": Grade(),
        "proof_base_grade": Grade(),
        "common_grade": Grade()
    }
    counts_grade = {
        "base_grade": 0,
        "proof_base_grade": 0,
        "common_grade": 0
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
        if counts_grade[label] == 0:
            grades[label].value = 0
            grades[label].name = "Нет оценки"
        else:
            grades[label].value = grades[label].value / counts_grade[label]
            grades[label].name = get_name_knowledge_grade_scale(grades[label].value)
    return grades["base_grade"], grades["proof_base_grade"], grades["common_grade"]

def get_group_users(request, knowledge_id: int):
    """
    Функция для получения группы пользователей

    - knowledge_id - id знания
    - возвращается группа пользователей
    """
    gender = request.GET.get("gender", None)
    age_from_to = {"min_age": 0, "max_age": 0}
    if request.GET.get("min_age", "0").isdigit() and \
            request.GET.get("max_age", "0").isdigit():
        age_from_to["min_age"] = int(request.GET.get("min_age", 0))
        age_from_to["max_age"] = int(request.GET.get("max_age", 0))

    profiles = None
    if gender:
        # получение всех профилей определенного пола
        profiles = Profile.objects.prefetch_related('user').filter(
            gender=gender,
            user__id__in=set(map(
                lambda x: x.user.id,
                KnowledgeGrade.objects.prefetch_related("user").filter(
                    knowledge__id=knowledge_id)))
        )
    if age_from_to["max_age"] > 0:
        if profiles is None:
            # получение всех профилей, которые оценивали знание
            profiles = Profile.objects.filter(user__id__in=set(map(
                lambda x: x.user.id,
                KnowledgeGrade.objects.prefetch_related("user").filter(
                    knowledge__id=knowledge_id))))
        # получение всех профилей, удовлятворяющих интервалу возраста
        now = datetime.date.today()
        min_age, max_age = datetime.timedelta(days=365*age_from_to["min_age"]),\
                           datetime.timedelta(days=365*age_from_to["max_age"])
        profiles = profiles.exclude(birthday_at=None)\
                             .annotate(age=(now - F("birthday_at")))\
                             .filter(age__gte=min_age, age__lt=max_age)
    if profiles is None:
        # получение всех пользователей, которые оценивали знание
        users = User.objects.filter(id__in=set(map(
            lambda x: x.user.id,
            KnowledgeGrade.objects.prefetch_related("user").filter(
                knowledge__id=knowledge_id))))
        return users
    users = list(map(lambda x: x.user, profiles))
    return users

def get_grade_values(request, users, relation: Relation) -> dict:
    """
    Получение все значения, по всей группе пользователей, оценки довода
    (proof_grade), общей оценки (common_grade), оценки знания
    (knowledge_grade), оценки связи (relation_grade)

    - users - группа пользователей
    - relation - связь
    - возвращается словарь, следующей структуры:
    {
        "proof_grade" (значения оценки довода),
        "common_grade" (значения общей оценки),
        "knowledge_grade" (значения оценки знания),
        "relation_grade" (значения оценки связи)
    }
    """
    copy_request = copy.copy(request)
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

def get_average_grades(request, users, relation: Relation) -> dict:
    """
    Вычисление средних значений оценок для связи

    - users - группа пользователей
    - relation - связь
    - возвращается словарь, следующей структуры:
    {
        "proof_grade" (среднее значение оценки довода),
        "common_grade" (среднее значение общей оценки),
        "knowledge_grade" (среднее значение оценки знания),
        "relation_grade" (среднее значение оценки связи)
    }

    """
    grade_values = get_grade_values(request, users, relation)
    for label in grade_values:
        grade_values[label] = mean(grade_values[label]) \
                              if len(grade_values[label]) >= 1 \
                              else 0

    grades = {
        "proof_grade": get_grade_from_knowledge_value(
            grade_values["proof_grade"]),
        "common_grade": get_grade_from_knowledge_value(
            grade_values["common_grade"]),
        "knowledge_grade": get_grade_from_knowledge_value(
            grade_values["knowledge_grade"]),
        "relation_grade": get_grade_from_relation_value(
            grade_values["relation_grade"]),
    }
    return grades

def get_average_grade(users, knowledge: Znanie) -> Grade:
    """
    Вычисление среднего значения оценки знания

    - users - группа пользователей
    - relation - связь
    - возвращается объект шкалы оценки знания
    """
    grade_values = []
    for user in users:
        base_knowledge_grade = KnowledgeGrade.objects.filter(
            knowledge=knowledge,
            user=user,
        ).first()
        if base_knowledge_grade:
            base_grade_value = base_knowledge_grade.grade.get_base_grade()
            if base_grade_value:
                grade_values.append(base_grade_value)
    average_grade = mean(grade_values) \
                    if len(grade_values) >= 1 \
                    else 0
    return get_grade_from_knowledge_value(average_grade)

def get_average_proof_base_and_common_grades(users, request, knowledge: Znanie) -> tuple[Grade, Grade]:
    """
    Вычисление среднего значения оценки доказательной базы и общей оценки
    знания

    - users - группа пользователей
    - knowledge - знание
    - возвращается среднее значение оценки доказательной связи и общей оценки
      знания
    """
    copy_request = copy.copy(request)
    proof_base_grades = []
    common_grades = []
    for user in users:
        copy_request.user = user
        common_grade_value, proof_base_value = knowledge.get_common_grades(
            request=copy_request)
        if proof_base_value:
            proof_base_grades.append(proof_base_value)
        if common_grade_value:
            common_grades.append(common_grade_value)
    average_proof_base_grade = mean(proof_base_grades) \
                               if len(proof_base_grades) >= 1 \
                               else 0
    average_common_grade = mean(common_grades) \
                           if len(common_grades) >= 1 \
                           else 0
    return get_grade_from_knowledge_value(average_proof_base_grade), \
           get_grade_from_knowledge_value(average_common_grade)

def get_average_proof(users, request, relation: Relation) -> Grade:
    """
    Вычисление среднего значения оценки довода среди группы пользователей

    - users - группа пользователей
    - relation - связь
    """
    copy_request = copy.copy(request)
    proof_grades = []
    for user in users:
        copy_request.user = user
        proof_grades.append(relation.get_proof_grade(
            copy_request,
            copy_request.GET.get("variant", 2)
        ))
    average_proof_grade_value = mean(proof_grades) \
                                if len(proof_grades) >= 1 \
                                else 0
    return get_grade_from_knowledge_value(average_proof_grade_value)

def get_group_relations(request, users, relations: list[Relation]) -> list[dict]:
    """
    Получение для всех связей - средних значений оценок связи и других
    данных о связи

    - users - группа пользователей
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
            grades = get_average_grades(request, users, relation)
            group_relations.append({
                "knowledge": relation.rz,
                "type_name": relation.tr.name,
                "proof_grade": grades["proof_grade"],
                "common_grade": grades["common_grade"],
                "knowledge_grade": grades["knowledge_grade"],
                "grade": grades["relation_grade"],
            })
    return group_relations
