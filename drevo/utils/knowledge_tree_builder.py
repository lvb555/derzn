from django.db.models import QuerySet
from drevo.models import Znanie, Relation, Category, Tz, Tr


class KnowledgeTreeBuilder:
    """
        Конструктор дерева знаний.
        Данный класс реализует функционал постройки дерева по знаниям и категориям.
    """
    def __init__(self, queryset: QuerySet[Znanie], show_only: Tr = None):
        self.queryset = queryset
        self.categories_data = {}
        self.knowledge = {}
        self._systemic_types = Tz.objects.filter(is_systemic=True).values_list('pk', flat=True)
        self.relations_name = {}  # {(<parent_id>, <child_id>): relation_name, }
        self.show_only = show_only  # Вид связи, который необходимо отображать на дереве для знаний из queryset
        self.category_rel_counts = dict()  # {category_pk: {'knowledge_count': 0, 'base_knowledge_count': 0}
        self.knowledge_rel_counts = dict()  # {knowledge: {'knowledge_count': 0, 'child_count': 0}

        relations = (
            Relation.objects
            .prefetch_related('bz', 'rz', 'tr', 'bz__tz', 'rz__tz')
            .filter(is_published=True, tr__is_systemic=False)
        )
        relations_data = {rel.rz.id: [] for rel in relations}
        for rel in relations:
            if self.show_only and rel.rz in queryset and rel.tr != self.show_only:
                continue
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
                relations_name: <Название вида связи между знаниями дерева>
                knowledge_rel_counts: <Показатели кол-ва всех и дочерних знаний для каждой ветви знания>
                category_rel_counts: <Показатели кол-ва всех и основных знаний для каждой ветви категории>
            }
        """
        tree_data = self.get_data_for_tree()
        categories_pk = [category for category in tree_data.keys() if category]
        categories = Category.tree_objects.exclude(is_published=False).filter(pk__in=categories_pk)
        active_nodes = list(Category.tree_objects.get_queryset_ancestors(categories, include_self=False))
        nodes_pk = list(cat.pk for cat in set(active_nodes)) + categories_pk
        category_nodes = (
            Category.tree_objects
            .exclude(is_published=False)
            .select_related('parent')
            .filter(pk__in=nodes_pk).distinct()
        )
        category_relations = {cat.id: [] for cat in category_nodes}
        for cat in category_nodes:
            if cat.parent and cat.parent.is_published:
                category_relations[cat.id].append(cat.parent.id)
        self._gather_knowledge_counter()
        self._gather_category_counter(category_relations, categories)
        context = {
            'tree_data': tree_data,
            'category_nodes': category_nodes,
            'relations_name': self.relations_name,
            'knowledge_rel_counts': self.knowledge_rel_counts,
            'category_rel_counts': self.category_rel_counts
        }
        return context

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

    def _gather_knowledge_counter(self) -> None:
        """
            Метод для получения показателей кол-ва всех и дочерних знаний для каждого знания дерева
        """
        knowledge_data = self.knowledge

        def count_knowledge(data: dict, cnt: int = 0) -> int:
            for values in data.values():
                cnt += count_knowledge(values) + len(values)
            return cnt

        def increase_knowledge_rel_count(knowledge_dict: dict) -> None:
            """
                Метод для увеличения показателей кол-ва всех и дочерних знаний с которыми связано текущее
            """
            for key, values in knowledge_dict.items():
                if len(values) == 0:
                    continue
                if key not in self.knowledge_rel_counts.keys():
                    self.knowledge_rel_counts[key] = {
                        'knowledge_count': len(values)+count_knowledge(values),
                        'child_count': len(values)
                    }
                increase_knowledge_rel_count(values)
        increase_knowledge_rel_count(knowledge_data)

    def _gather_category_counter(self, category_relations: dict, base_categories: QuerySet[Category]) -> None:
        """
            Метод для получения показателей кол-ва всех и основных знаний, которые относятся к категориям дерева
        """
        def count_base_knowledge(data: dict, cnt: int = 0) -> int:
            """
                Метод для подсчёта основных знаний (тех у которых есть категория)
            """
            for key, value in data.items():
                if key.category_id:
                    cnt += 1
                cnt += sum(1 for knowledge in value.keys() if knowledge.category_id)
                count_base_knowledge(value, cnt)
            return cnt

        # Получаем данные о знаниях, которые привязаны к категориям
        category_data = {cat.id: self.categories_data.get(cat.id) for cat in base_categories}

        # Собираем показатели для тех категорий от которых строятся знания
        for category, values in category_data.items():
            knowledge_count = len(values)
            base_knowledge_count = 0
            kns = []
            for base_kn in values:
                kns.extend(base_kn.keys())

            for base_kn in kns:
                if base_kn.category_id:
                    base_knowledge_count += 1
                base_knowledge_count += count_base_knowledge(self.knowledge.get(base_kn))
                kn_data = self.knowledge_rel_counts.get(base_kn)
                if not kn_data:
                    continue
                knowledge_count += self.knowledge_rel_counts.get(base_kn)['knowledge_count']

            self.category_rel_counts[category] = {
                'knowledge_count': knowledge_count,
                'base_knowledge_count': base_knowledge_count
            }
        # Дополняем словарь родителями тех категорий от которых строятся знания
        for category in category_relations.keys():
            if category not in self.category_rel_counts:
                self.category_rel_counts[category] = {'knowledge_count': 0, 'base_knowledge_count': 0}

        def count_parent_data(category_obj: Category, kn_count=0, base_kn_count=0):
            """
                Метод для посчёта показателей категорий родителей на основе данных их дочерних категорий
            """
            parents = category_relations.get(category_obj)

            for parent in parents:
                self.category_rel_counts[parent]['knowledge_count'] += kn_count
                self.category_rel_counts[parent]['base_knowledge_count'] += base_kn_count
                count_parent_data(parent, kn_count, base_kn_count)

        for category in category_data.keys():
            knowledge_count, base_knowledge_count = self.category_rel_counts[category].values()
            count_parent_data(category, knowledge_count, base_knowledge_count)
