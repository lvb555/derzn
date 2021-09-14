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
