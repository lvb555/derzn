from django.db.models import QuerySet
from drevo.models import Znanie, Relation, Category, Tz


class KnowledgeTreeBuilder:
    """
        Конструктор дерева знаний.
        Данный класс реализует функционал постройки дерева по знаниям и категориям.
    """
    def __init__(self, queryset: QuerySet[Znanie]):
        self.queryset = queryset
        self.categories_data = {}
        self.knowledge = {}
        self._systemic_types = Tz.objects.filter(is_systemic=True).values_list('pk', flat=True)
        self.relations_name = {}  # {(<parent_id>, <child_id>): relation_name, }

        relations = (
            Relation.objects
            .prefetch_related('bz', 'rz', 'tr', 'bz__tz', 'rz__tz')
            .filter(is_published=True, tr__is_systemic=False)
        )
        relations_data = {rel.rz.id: [] for rel in relations}
        for rel in relations:
            self.relations_name.update({(rel.bz.id, rel.rz.id): rel.tr.name})
            relations_data[rel.rz.id].append(rel.bz)
        self.relations_data = relations_data

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
        categories_pk = [category for category in tree_data.keys() if category]
        categories = Category.tree_objects.exclude(is_published=False).filter(pk__in=categories_pk)
        active_nodes = list(Category.tree_objects.get_queryset_ancestors(categories, include_self=False))
        nodes_pk = list(cat.pk for cat in set(active_nodes)) + categories_pk
        category_nodes = Category.tree_objects.exclude(is_published=False).filter(pk__in=nodes_pk).distinct()
        return dict(tree_data=tree_data, category_nodes=category_nodes, relations_name=self.relations_name)

    def get_data_for_tree(self) -> dict:
        """
            Метод для разделения данных знаний на категории \n
            Возвращает вложенный словарь: \n
            {
                category_pk_1: [{
                    base_knowledge_1: {
                        knowledge_1: {knowledge_1_1: {}, knowledge_1_2: {},},
                        knowledge_2: {knowledge_2_1: {}, knowledge_2_2: {},}
                    },
                }],
            }
        """
        self._gather_knowledge_relations()

        for base_knowledge, related_knowledge in self.knowledge.items():
            if not base_knowledge.category_id:
                continue
            category = base_knowledge.category_id
            if category in self.categories_data.keys():
                self.categories_data[category].append({base_knowledge: related_knowledge})
            else:
                self.categories_data[category] = [{base_knowledge: related_knowledge}]
        return self.categories_data

    def _gather_knowledge_relations(self) -> None:
        """
            Метод для сбора последовательного списка связанных знаний для каждого знания
        """
        ancestors_knowledge = self._get_ancestors_for_knowledge_list()
        for ancestors in ancestors_knowledge:
            self._build_tree_data(ancestors)

    def _build_tree_data(self, knowledge_list: list) -> None:
        """
            Метод, который рекурсивно обходит текущие данные для дерева, следуя цепочке связей знаний,
            которые передаются в виде списка. Если такого знания нет в данных, то оно добавляется
        """
        def check_exists(tree: dict, knowledge: list) -> None:
            while knowledge:
                parent = knowledge.pop(0)
                if parent.tz_id in self._systemic_types:
                    continue
                if parent not in tree:
                    tree[parent] = {}
                check_exists(tree[parent], knowledge)
            return

        knowledge_data = knowledge_list.copy()
        check_exists(self.knowledge, knowledge_data)

    def _get_ancestors_for_knowledge_list(self) -> list[list[Znanie]]:
        """
            Метод для получения предков для списка знаний \n
            На выходе получается двумерный список связей всех полученных знаний от базового знания до текущего
        """
        raw_data = {knowledge: self.relations_data.get(knowledge.id) for knowledge in self.queryset}
        rel_path_list = []
        for rz, relation_data in raw_data.items():
            if not relation_data:
                rel_path_list.append([rz])
                continue
            for bz in relation_data:
                if not self.relations_data.get(bz.id):
                    rel_path_list.append([bz, rz])
                    continue
                rel_path_list.extend([path[::-1] + [rz] for path in self._get_all_relations(bz, self.relations_data)])
        return rel_path_list

    @staticmethod
    def _get_all_relations(base_knowledge: Znanie, base_data: dict) -> list[list]:
        """
            Метод для получения двумерного списка со всеми путями связей от текущего знания до базового
        """
        paths = []
        visited = set()

        def get_paths(node, path):
            if node in visited:
                return
            visited.add(node)
            path.append(node)
            if node.id not in base_data:
                paths.append(path)
                return
            for neighbour in base_data[node.id]:
                get_paths(neighbour, path.copy())

        get_paths(base_knowledge, [])
        return paths
