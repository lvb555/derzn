"""
Тесты для поведения оберток Знания
"""

from django.test import TestCase

from users.models import User
from .models import Author, AuthorType, Category, Tr, Tz, Znanie
from .utils.knowledge_proxy import TableProxy


class TestTableProxy(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        User.objects.create(username="TestUser", password="testpassword")
        AuthorType.objects.create(name="TestAuthorType")
        test_author_type = AuthorType.objects.get(id=1)
        Author.objects.create(
            name="TestAuthor", info="Test info", atype=test_author_type
        )

        Category.objects.create(
            name="TestCategory", content="Test content", is_published=True
        )

        # для тестирования поведения Таблицы
        Tz.objects.create(name="Таблица")
        Tz.objects.create(name="Значение")

        Tr.objects.create(name="Состав")

    def test_table(self):
        category = Category.objects.get(id=1)
        author = Author.objects.get(id=1)
        user = User.objects.get(id=1)

        value_1 = Znanie.objects.create(
            name="Value_1",
            category=category,
            tz=Tz.t_('Значение'),
            content="Test content",
            author=author,
            user=user,
        )
        value_2 = Znanie.objects.create(
            name="Value_2",
            category=category,
            tz=Tz.t_('Значение'),
            content="Test content",
            author=author,
            user=user,
        )

        table_1 = Znanie.objects.create(
            name="TestTable_1",
            category=category,
            tz=Tz.t_('Таблица'),
            content="Test content",
            author=author,
            user=user,
        )

        tbl = TableProxy(table_1)

        # тест на пустую таблицу
        self.assertTrue(tbl.is_zero_table())
        self.assertTrue(tbl.is_empty_table())

        header_old = {
            'group_row': 'Заголовок строк',
            'group_col': 'Заголовок колонок',
            'cols': [{'id': 2, 'name': 'колонка 1'}, {'id': 0, 'name': 'колонка 2'}],
            'rows': [{'id': 0, 'name': 'Строка 1'}, {'id': 0, 'name': 'Строка 2'}]
        }

        tbl.update_header(header_old)
        header_new = tbl.get_header()

        self.assertTrue(tbl.headers_is_eq(header_old, header_new))

        # проверяем что значение установлено
        self.assertEquals(header_old['rows'][0]['id'], 1)
        self.assertEquals(header_old['rows'][1]['id'], 2)
        self.assertEquals(header_old['cols'][1]['id'], 3)

        values = tbl.get_cells(in_list=True)
        self.assertEquals(values, [])

        matrix = tbl.get_cells(in_list=False)
        self.assertEquals(matrix, [[None, None], [None, None]])

        # проверяем на пустую запись
        tbl.update_values(header_old, [], user)

        # проверяем на запись одного значения
        data = [{'col': 0, 'row': 0, 'id': value_1.pk}]
        tbl.update_values(header_old, data, user)

        header, values = tbl.get_header_and_cells()
        self.assertEquals(header, header_old)
        self.assertEquals(values, [{'row': 0, 'col': 0, 'id': value_1.pk, 'name': value_1.name}])

        matrix = tbl.get_cells(in_list=False)
        self.assertEquals(matrix, [[value_1, None], [None, None]])

        # проверяем на два значения
        data = [{'col': 0, 'row': 0, 'id': value_1.pk}, {'col': 1, 'row': 0, 'id': value_2.pk}]
        tbl.update_values(header_old, data, user)

        matrix = tbl.get_cells(in_list=False)
        self.assertEquals(matrix, [[value_1, value_2], [None, None]])

        # тест на замену данных
        data = [{'col': 0, 'row': 0, 'id': value_1.pk}, {'col': 1, 'row': 1, 'id': value_2.pk}]
        tbl.update_values(header_old, data, user)

        matrix = tbl.get_cells(in_list=False)
        self.assertEquals(matrix, [[value_1, None], [None, value_2]])

        # тест на замену заголовка и порядка
        header = {
            'group_row': '',
            'group_col': '',
            'cols': [{'id': 3, 'name': 'колонка 1'}, {'id': 2, 'name': 'колонка 2'}],
            'rows': [{'id': 2, 'name': 'Строка 1'}, {'id': 1, 'name': 'Строка 2'}]
        }

        tbl.update_header(header)
        matrix = tbl.get_cells(in_list=False)
        self.assertEquals(matrix, [[value_2, None], [None, value_1]])

        # убираем одну строку
        header = {
            'group_row': '',
            'group_col': '',
            'cols': [{'id': 3, 'name': 'колонка 1'}],
            'rows': [{'id': 2, 'name': 'Строка 1'}, {'id': 1, 'name': 'Строка 2'}]
        }

        tbl.update_header(header)
        matrix = tbl.get_cells(in_list=False)
        self.assertEquals(matrix, [[value_2], [None]])

        header = {
            'group_row': '',
            'group_col': '',
            'cols': [{'id': 3, 'name': 'колонка 1'}, {'id': 2, 'name': 'колонка 2'}],
            'rows': [{'id': 2, 'name': 'Строка 1'}, {'id': 1, 'name': 'Строка 2'}]
        }

        tbl.update_header(header)
        matrix = tbl.get_cells(in_list=False)
        self.assertEquals(matrix, [[value_2, None], [None, None]])

        # делаем новую структуру
        header = {
            'group_row': '',
            'group_col': '',
            'cols': [{'id': 0, 'name': 'колонка 1'}, {'id': 0, 'name': 'колонка 2'}],
            'rows': [{'id': 0, 'name': 'Строка 1'}, {'id': 0, 'name': 'Строка 2'}]
        }

        tbl.update_header(header)
        matrix = tbl.get_cells(in_list=False)
        self.assertEquals(matrix, [[None, None], [None, None]])