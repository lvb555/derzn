# drevo/tests/test_sample.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from drevo.models import Znanie, Category, Tz
from drevo.utils.knowledge_tree_builder import KnowledgeTreeBuilder

User = get_user_model()


class KnowledgeTreeBuilderSampleTest(TestCase):
    def setUp(self):
        # Создаем тестового пользователя
        self.user = User.objects.create_user(username='testuser', password='testpass')

        # Создаем тестовую категорию
        self.category = Category.objects.create(name='Test Category', is_published=True)

        # Создаем тестовый тип знания
        self.tz_simple = Tz.objects.create(name='Simple', is_systemic=False)

        # Создаем знания для теста, обязательно передавая пользователя
        self.parent = Znanie.objects.create(
            name='Parent',
            category=self.category,
            tz=self.tz_simple,
            user=self.user
        )

        self.child1 = Znanie.objects.create(
            name='Child1',
            category=self.category,
            tz=self.tz_simple,
            user=self.user
        )

        self.child2 = Znanie.objects.create(
            name='Child2',
            category=self.category,
            tz=self.tz_simple,
            user=self.user
        )

        # Будем тестировать единственный вариант цепочки: Parent -> Child1 -> Child2
        self.ancestors_chain = [[self.parent, self.child1, self.child2]]

    def fake_get_ancestors(self):
        """
        Фиктивный метод, возвращающий подготовленную для теста цепочку знаний.
        """
        return self.ancestors_chain

    def test_get_data_for_tree(self):
        # Фильтруем знания для теста
        qs = Znanie.objects.filter(pk__in=[self.parent.pk, self.child1.pk, self.child2.pk])

        # Создаем экземпляр построителя дерева
        builder = KnowledgeTreeBuilder(
            queryset=qs,
            show_complex=False,
            edit_mode=False,
            empty_categories=False,
        )
        # Подменяем метод получения цепочек на фиктивный метод, возвращающий тестовые цепочки
        builder._get_ancestors_for_knowledge_list = self.fake_get_ancestors

        # Получаем дерево
        tree = builder.get_data_for_tree()

        # Ожидаемая структура дерева:
        # {
        #   <category.pk>: [{
        #       parent: {
        #           child1: {
        #               child2: {}
        #           }
        #       }
        #   }]
        # }
        expected_tree = {
            self.category.pk: [{
                self.parent: {
                    self.child1: {
                        self.child2: {}
                    }
                }
            }]
        }

        self.assertEqual(self.flatten_tree(tree), self.flatten_tree(expected_tree))

    def flatten_tree(self, tree):
        """
        Рекурсивное преобразование дерева в формат, удобный для сравнения.
        Если узел является объектом, используем его pk, если это int — оставляем как есть.
        Также обрабатываем списки.
        """
        if isinstance(tree, list):
            return [self.flatten_tree(item) for item in tree]
        elif isinstance(tree, dict):
            flat = {}
            for key, subtree in tree.items():
                # Если ключ имеет атрибут pk, используем его; иначе — используем ключ как есть.
                key_id = key.pk if hasattr(key, 'pk') else key
                flat[key_id] = self.flatten_tree(subtree)
            return flat
        else:
            return tree

