"""
Функции для построения деревьев отношений.
"""

from .models import Author, Relation, Znanie, Category


def get_category_for_knowledge(knowledge: Znanie) -> [None, Category]:
    """
    Возвращает категорию, к которой принадлежит знание. 
    Если категория назначена непосредственно (основное знание), то возвращается она.
    Если категории не назначена (дополнительное знание), то производится
    рекурсивный поиск основного знания по цепочке через сущность Relation.
    Поиск останавливается и возвращается None, если очередное знание в цепочке
    окажется неопубликованным.
    """
    if knowledge.category and knowledge.category.is_published and knowledge.is_published:
        return knowledge.category
    elif knowledge.is_published:
        # ищем связь с другим знанием и рекурсивно получаем категорию для базового знания
        relation = Relation.objects.filter(rz=knowledge).first()
        if relation and relation.is_published:
            base_knowledge = relation.bz
            return get_category_for_knowledge(base_knowledge)
        else:
            return None
    else:
        return None


def get_ancestors_for_knowledge(knowledge: Znanie) -> list:
    """
    Возвращает список знаний, через которые данное знание связано с 
    основным знанием (цепочку знаний). Основное знание включается в список.
    Если данное знание является основным, то возвращается пустой список.

    Цепочка возвращается в иерархическом порядке, т.е. основное знание 
    (если имеется) - первое в списке, а знание, связанное непосредственно с текущим, 
    - последнее.
    """
    chain = []
    def get_ancestors(knowledge: Znanie):
        """
        Рекурсивно ищет предков текущего знания вплоть до основного знания,
        попутно заполняя список chain найденными предками.
        """
        if knowledge.category and knowledge.category.is_published and knowledge.is_published:
            return None
        elif knowledge.is_published:
            # ищем связь с другим знанием и рекурсивно получаем следюущее знание в цепочке
            relation = Relation.objects.filter(rz=knowledge).first()
            if relation and relation.is_published:
                base_knowledge = relation.bz
                chain.append(base_knowledge)
                return get_ancestors(base_knowledge)
            else:
                return None
        else:
            return None

    get_ancestors(knowledge)
    return chain[::-1]


def get_children_for_knowledge(knowledge):
    """
    Возвращает queryset знаний, для которых непосредственным предком
    является knowledge.
    """
    if knowledge.is_published:
        return Znanie.published.filter(related__bz=knowledge)
    else:
        return None


def get_siblings_for_knowledge(knowledge: Znanie) -> [None, list]:
    """
    Возвращает список знаний, имеющих того же предка, что
    и knowledge.
    """
    if knowledge.category and knowledge.category.is_published and knowledge.is_published:
        return list(Znanie.published.filter(category=knowledge.category).exclude(pk=knowledge.pk))
    elif knowledge.is_published:
        # находим базовое знание
        # TODO связь znanie - Relation д.б. единственно возможной.
        relation = Relation.objects.filter(rz=knowledge).first()
        if relation and relation.is_published:
            base_knowledge = relation.bz
            return list(Znanie.published.filter(related__bz=base_knowledge).
            exclude(pk=knowledge.pk).exclude(pk=base_knowledge.pk))
        else:
            return None
    else:
        return None