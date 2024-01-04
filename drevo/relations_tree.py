"""
Функции для построения деревьев отношений.
"""
from .models import Author, Relation, Znanie, Category, Tr
import collections


def get_knowledges_by_categories(knowledges_queryset):
    """
    Распределяет дополнительные знания по категориям.
    Возвращает список категорий, к которым относятся входные знания,
    и словарь, в котором ключ - категория, а значение - 
    словарь со списками осн. и доп. знаний в этой категории:
    {
        category_name : {
            'base' : [список основных знаний],
            'additional' : [список дополнительных знаний],
        }
    }
    """
    # инициализируем словарь
    # используем defaultdict, чтобы при первом обращении по
    # ключу (еще несуществующему) возвращался пустой словарь
    knowledges_by_categories = collections.defaultdict(dict)

    # получаем категории для знаний автора
    for knowledge in knowledges_queryset:

        # получаем категорию для текущего знания
        # если в результате поиска категории нет, в словарь
        # добавляет псевдокатегория с именем 'None'
        category = get_category_for_knowledge(knowledge)
        category_name = category.name if category else 'None'

        # открываем словарь с категорией текущего знания
        knowledges = knowledges_by_categories[category_name]
        # сразу создаем два ключа и присоединяем к ним по пустому списку,
        # один для основных знаний, другой для дополнительных.
        # это позволит обойтись далее без проверок на существование этих списков,
        # а в шаблоне при отсутствии соотв. знаний в категории будет выводится пустой лист.
        if not 'base' in knowledges:
            knowledges['base'] = []
        if not 'additional' in knowledges:
            knowledges['additional'] = []

        # если категория указана, то добавляем знание в список
        # основных знаний, если нет - то дополнительных
        if knowledge.category:
            knowledges['base'].append(knowledge)
        else:
            knowledges['additional'].append(knowledge)

    # список id категорий, в которых есть знания автора
    ids = list(knowledges_by_categories.keys())
    if 'None' in ids:
        ids.remove('None')
    categories_id_list = [Category.objects.get(name=x).id for x in ids]

    # формируем список категорий в соответствии с порядком, заданным mptt
    
    categories = (Category.tree_objects
                    .filter(pk__in=categories_id_list)
                    .exclude(is_published=False))


    return categories, knowledges_by_categories


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
        relation = Relation.objects.filter(rz=knowledge,
                                           is_published=True).exclude(tr__is_systemic=True).first()
        if relation:
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
            # ищем связь с другим знанием и рекурсивно получаем следующее знание в цепочке
            relation = Relation.objects.filter(rz=knowledge,
                                               is_published=True).exclude(tr__is_systemic=True).first()
            if relation:
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
        return Znanie.published.filter(related__bz=knowledge,
                                       related__is_published=True
                                       ).order_by('related__order')
    else:
        return None


def get_children_by_relation_type_for_knowledge(knowledge):

    def sort_by_relation_type(s):
        relation_type = Tr.objects.get(name=s[0])
        order = relation_type.order
        return order if order else 0

    def sort_by_knoweledge_type(s):
        order_tz = s.tz.order
        order_z = s.order or 0
        return order_tz, order_z

    children = get_children_for_knowledge(knowledge)
    if not children:
        return None
    children_grouped_by_relation_type = {}
    for child in children:
        relation = Relation.objects.filter(bz=knowledge, rz=child).first()
        children_grouped_by_relation_type.setdefault(
            relation.tr, []).append(child)

    # Сортировка по видам знания и его параметру order
    for relation_type, children in children_grouped_by_relation_type.items():
        children.sort(key=sort_by_knoweledge_type)

    # Сортировка по видам связи
    children_sorted_by_relation_order = sorted(children_grouped_by_relation_type.items(),
                                               key=sort_by_relation_type)
    return dict(children_sorted_by_relation_order)


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
        relation = Relation.objects.filter(rz=knowledge,
                                           is_published=True).exclude(tr__is_systemic=True).first()
        if relation:
            base_knowledge = relation.bz
            return list(Znanie.published.filter(related__bz=base_knowledge,
                                                related__is_published=True).
                        exclude(pk=knowledge.pk).
                        exclude(pk=base_knowledge.pk))
        else:
            return None
    else:
        return None


def get_descendants_for_knowledge(knowledge: Znanie) -> list:
    """
    Возвращает QuerySet знаний, которые являются потомками заданного знания
    """

    list_of_descendants = []

    def get_all(queryset):
        """
        Рекурсивно ищет потомков текущего знания до тех пор,
        пока функция get_children_for_knowledge не вернет None
        """
        for every_child in list(queryset):
            founded = get_children_for_knowledge(every_child)
            if founded:
                list_of_descendants.append(founded)
                get_all(founded)
        return list_of_descendants
    get_all([knowledge])
    q1 = Znanie.objects.none()
    for i in list_of_descendants:
        q2 = q1 | i
        q1 = q2
    return q1
