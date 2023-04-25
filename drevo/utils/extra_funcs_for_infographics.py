from .extra_funcs_for_group_knowledge_grade import get_average_proof, Grade
from drevo.models.relation import Relation
from drevo.models.knowledge_grade import KnowledgeGrade
from drevo.models.knowledge_grade_scale import KnowledgeGradeScale
from drevo.models.knowledge_grade_color import KnowledgeGradeColor

ind_element_tree = 0


def get_color_from_hsl(knowledge_type: bool, value: float) -> str:
    """
    Получение цвета для html из значения оценки знания
    """
    range_color = KnowledgeGradeColor.objects.get(
        knowledge_type=knowledge_type)
    saturation = (range_color.saturation*100)/255
    light = 100 - ((
        (range_color.high_light - range_color.low_light) \
        * value + range_color.low_light) * 100) / 255
    color = f"hsl({range_color.hue}, {saturation}%, {light}%)"
    return color

def get_colors_and_value_from_knowledge(request, relation: Relation, lvl_against: int,
                              father_relation: Relation | None, is_group_knowledge: bool,
                              users) -> tuple[str, str, float]:
    """
    Получение цвета и значение оценки довода знания

    - relation - связь от родительского знания к знанию, для которого
                 определяется цвет
    - lvl_against - уровень довода против, т.е. если, к примеру, родитель
                    довод против и знание, для которого определяем цвет,
                    то будет уровень равнятся 2
    - father_relation - родительская связь
    - is_group_knowledge - переменная отвечающая на вопрос групповая ли это
                           оценка знания
    - users - группа пользователей
    """
    bg_color = "#FFFFFF"
    font_color = "#000000"
    proof_grade = Grade(name="Нет оценки", value=0.0)
    try:
        if not is_group_knowledge:
            proof_grade.value = relation.get_proof_grade(
                request,
                request.GET.get("variant", 1)
            )
        else:
            proof_grade.value = get_average_proof(users, request, relation).value
        grade = KnowledgeGradeScale.get_grade_object(proof_grade.value)
        if not proof_grade.value:
            proof_grade.name = "Нет оценки"
        else:
            proof_grade.name = grade.name
        father_argument_type = False
        if father_relation is not None:
            father_argument_type = father_relation.tr.argument_type

        if any((all((not father_argument_type, relation.tr.argument_type)),
                all((father_argument_type,
                     any((all((not relation.tr.argument_type, lvl_against % 2 == 0)),
                          all((not relation.tr.argument_type, lvl_against % 2 != 0))
                          )))))):
            bg_color = get_color_from_hsl(1, proof_grade.value)
        elif any((all((not father_argument_type,
                       not relation.tr.argument_type)),
                  all((father_argument_type,
                       any((all((relation.tr.argument_type, lvl_against % 2 == 0)),
                            all((relation.tr.argument_type, lvl_against % 2 != 0))
                            )))))):
            bg_color = get_color_from_hsl(0, proof_grade.value)
    except:
        pass
    return bg_color, font_color, proof_grade

def get_elements_tree(index_element_tree: int, request, relations: list[Relation],
                      lvl_up: bool = False, lvl_against: int = -1,
                      father_relation: Relation | None = None,
                      is_group_knowledge: bool = False, users = None) -> list[dict]:
    """
    Получение элементов дерева

    - index_element_tree - индекс элемента дерева
    - relations - связи, с помощью которых должны получить элементы дерева
    - lvl_up - переменная для определения нужно ли по дереву подниматься
               на уровень выше
    - lvl_against - уровень довода против, т.е. если, к примеру, родитель
                    довод против и знание, для которого определяем цвет,
                    то будет уровень равнятся 2
    - father_relation - родительская связь
    - is_group_knowledge - переменная отвечающая на вопрос групповая ли это
                           оценка знания
    - возвращается лист из словарей, который имеет следующую структуру:
      [
        {
          "name": имя знания,
          "url": ссылка до страницы знания,
          "proof_value": значение оценки довода,
          "bg_color": цвет фона,
          "font_color": цвет шрифта,
          "for_or_against": буква обозначающая какой это довод - за или
                            против,
          "has_childrens": есть ли у этого знания сыновья,
          "id": идентификатор элемента дерева,

          необязательные параметры:
          "lvl_up": переменная для определения нужно ли по дереву
                    подниматься на уровень выше,
          "lvl_down": переменная для определения нужно ли по дереву
                      подниматься на уровень ниже
        },
        ...
      ]
    """
    global ind_element_tree
    ind_element_tree = index_element_tree

    tree = []
    for relation in relations:
        if not relation.tr.argument_type:
            lvl_against = -1
        elif relation.tr.argument_type and (father_relation is None or not father_relation.tr.argument_type):
            lvl_against = 1
        elif relation.tr.argument_type and father_relation.tr.argument_type:
            lvl_against += 1

        if relation.tr.is_argument:
            knowledge = relation.rz
            childrens_knowledge = knowledge.base.filter(
                tr__is_argument=True,
                rz__tz__can_be_rated=True,
            ).order_by('tr__name')
            bg_color, font_color, proof_grade = get_colors_and_value_from_knowledge(
                request, relation, lvl_against, father_relation, is_group_knowledge,
                users)
            tree.append({
                "name": knowledge.name,
                "url": knowledge.get_absolute_url(),
                "proof_value": proof_grade.value,
                "proof_grade": proof_grade.name,
                "bg_color": bg_color,
                "font_color": font_color,
                "lvl_up": lvl_up,
                "for_or_against": "К" if relation.tr.argument_type else "А",
                "has_childrens": bool(childrens_knowledge),
                "id": ind_element_tree,
            })
            index_element_tree += 1

            if lvl_up:
                lvl_up = False

            if childrens_knowledge:
                tree += get_elements_tree(index_element_tree, request,
                                          childrens_knowledge, True, lvl_against,
                                          relation, is_group_knowledge, users)
                tree.append({"lvl_down": True})
    return tree
