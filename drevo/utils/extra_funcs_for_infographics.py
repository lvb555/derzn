from .extra_funcs_for_group_knowledge_grade import get_group_users, get_average_grade
from drevo.models.relation import Relation
from drevo.models.knowledge_grade import KnowledgeGrade


def get_colors_from_knowledge(request, relation: Relation, lvl_against: int,
                              father_relation: Relation | None, is_group_knowledge: bool,
                              users) -> tuple[str, str]:
    """
    Получение цвета знания

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
    try:
        if not is_group_knowledge:
            grade = KnowledgeGrade.objects.get(
                knowledge=relation.rz,
                user=request.user,
            ).grade
        else:
            grade = get_average_grade(users, relation)
        father_argument_type = False
        if father_relation is not None:
            father_argument_type = father_relation.tr.argument_type

        if any((all((not father_argument_type, relation.tr.argument_type)),
                all((father_argument_type,
                     any((all((not relation.tr.argument_type, lvl_against % 2 == 0)),
                          all((not relation.tr.argument_type, lvl_against % 2 != 0))
                          )))))):
            bg_color = grade.contraargument_color_background
            font_color = grade.contraargument_color_font
        elif any((all((not father_argument_type,
                       not relation.tr.argument_type)),
                  all((father_argument_type,
                       any((all((relation.tr.argument_type, lvl_against % 2 == 0)),
                            all((relation.tr.argument_type, lvl_against % 2 != 0))
                            )))))):
            bg_color = grade.argument_color_background
            font_color = grade.argument_color_font
    except KnowledgeGrade.DoesNotExist:
        pass
    return bg_color, font_color

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
            childrens_knowledge = Relation.objects.filter(bz=knowledge)
            bg_color, font_color = get_colors_from_knowledge(
                request, relation, lvl_against, father_relation, is_group_knowledge,
                users)
            tree.append({
                "name": knowledge.name,
                "bg_color": bg_color,
                "font_color": font_color,
                "lvl_up": lvl_up,
                "for_or_against": "К" if relation.tr.argument_type else "А",
                "has_childrens": bool(childrens_knowledge),
                "id": index_element_tree,
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
