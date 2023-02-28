from django.db.models import QuerySet
from drevo.models import Znanie, Relation, Category
from drevo.relations_tree import get_ancestors_for_knowledge, get_category_for_knowledge


class KnowledgeTreeBuilder:
    """
        Конструктор дерева знаний.
        Данный класс реализует функционал постройки дерева по знаниям и категориям.
    """
    def __init__(self, queryset: QuerySet[Znanie]):
        self.queryset = queryset
        self.categories_data = dict()
        self.knowledge = dict()

    def get_nodes_data_for_tree(self) -> dict:
        """
            Метод для получения всех данных узлов, необходимых для построения дерева знаний и категорий \n
            Данные для постройки дерева на выходе: \n
            {
                tree_data: <Вложенный словарь категорий и знаний>,
                category_nodes: <Узлы для построения дерева категорий>
            }
        """
        tree_data = self.get_data_for_tree()
        categories_pk = [category.pk for category in tree_data.keys() if category]
        categories = Category.tree_objects.exclude(is_published=False).filter(pk__in=categories_pk)
        active_nodes = list()
        for cat in categories:
            active_nodes.extend(list(cat.get_ancestors()))
        nodes_pk = list(cat.pk for cat in set(active_nodes)) + categories_pk
        category_nodes = Category.tree_objects.exclude(is_published=False).filter(pk__in=nodes_pk).distinct()
        return dict(tree_data=tree_data, category_nodes=category_nodes)

    def get_data_for_tree(self) -> dict:
        """
            Метод для разделения данных знаний на категории \n
            Возвращает вложенный словарь: \n
            {
                category_1: [{
                    base_knowledge_1: {
                        knowledge_1: {knowledge_1_1: {}, knowledge_1_2: {},},
                        knowledge_2: {knowledge_2_1: {}, knowledge_2_2: {},}
                    },
                }],
            }
        """
        self._gather_knowledge_relations()

        for base_knowledge, related_knowledge in self.knowledge.items():
            category = get_category_for_knowledge(base_knowledge)
            # Если основное знание не относится к какой либо категории, то получаем категорию его связанных знаний
            if not category:
                category = self._get_category(related_knowledge)
                if not category:
                    continue

            if category in self.categories_data.keys():
                self.categories_data[category].append({base_knowledge: related_knowledge})
            else:
                self.categories_data[category] = [{base_knowledge: related_knowledge}]
        return self.categories_data

    def _gather_knowledge_relations(self) -> None:
        """
            Метод для сбора последовательного списка связанных знаний для каждого знания
        """
        knowledge_data = dict()
        for knowledge in self.queryset:
            # Получаем цепочку знаний до текущего знания
            kn_data = get_ancestors_for_knowledge(knowledge)
            kn_data.append(knowledge)
            self._build_tree_data(kn_data)
            if kn_data:
                knowledge_data[kn_data[0]] = kn_data

        for related_knowledge in knowledge_data.values():
            # Получаем цепочку знаний которые идут после
            if len(related_knowledge) == 1:
                continue
            last_knowledge = related_knowledge[-1]
            after_kns = list()
            while True:
                rel = Relation.objects.filter(bz=last_knowledge).first()
                if not rel:
                    break
                after_kns.append(rel.rz)
                last_knowledge = rel.rz
            self._build_tree_data(after_kns)

    def _build_tree_data(self, knowledge_list: list) -> None:
        """
            Метод, который рекурсивно обходит текущие данные для дерева, следуя цепочке связей знаний,
            которые передаются в виде списка. Если такого знания нет в данных, то оно добавляется
        """
        def check_exists(tree: dict, knowledge: list) -> None:
            while knowledge:
                parent = knowledge.pop(0)
                if parent in tree:
                    check_exists(tree[parent], knowledge)
                else:
                    tree[parent] = dict()
                    check_exists(tree[parent], knowledge)
            return
        check_exists(self.knowledge, knowledge_list)

    @staticmethod
    def _get_category(knowledge_data: dict):
        """
            Метод, который рекурсивно обходит данные для дерева, чтобы получить категорию к которой относятся данные
            того или иного основного знания
        """
        def search_knowledge_with_category(branch: dict):
            for base_knowledge, related_knowledge in branch.items():
                cat = get_category_for_knowledge(base_knowledge)
                if cat:
                    return cat
                search_knowledge_with_category(related_knowledge)
            return None
        return search_knowledge_with_category(knowledge_data)
