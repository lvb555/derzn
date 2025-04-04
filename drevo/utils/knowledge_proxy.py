"""
Объекты - обертки для знаний, представляющие дополнительный функционал
"""

import json
from collections import Counter

from drevo.models import Author, Relation, Tr, Tz, Znanie
from users.models import User


class KnowledgeProxyError(Exception):
    pass


# текущая версия формата метаданных
CURRENT_TABLE_VERSION = 3


class TableProxy:
    """
    Для упрощения работы с таблицами
    Описание идеи:
    У модели Znanie есть поле Метаданные.
    В поле метаданные в JSON словаре по ключу 'table' хранится описание структуры таблицы типа
    {
        'version': 2, # текущая версия структуры - подозреваю, что потребуется скоро :)
        'group': 'Заголовок верхний левый угол таблицы',
        'group_row': 'Заголовок строк',
        'group_col': 'Заголовок колонок',
        'cols': [{'id':12, 'name': 'колонка 1'}],
        'rows': [{'id':10, 'name': 'Строка 1'}],
        cells: {'row_id:col_id': {'state':1, 'value': 'текст в ячейке', 'user_id': 'идентификатор пользователя'}, ...}
        - статус ячейки, текст ячейки, который хранится в метаданных и id автора - нужно для проверки прав на изменения
    }
    порядок колонок/строк важен и задает их порядок при просмотре таблицы
    id новых колонок/строк высчитываются как максимальный id колонок/строк +1

    Ячейки связываются с таблицей связью типа 'Состав'
    В поле метаданные в JSON словаре по ключу 'cell' записывается данные о позиции ячейки
    {'cell': {'row': id_row, 'col': id_col}
    использование позиционирования ячеек по идентификатору колонки/строк вместо относительного позиционирования
    типа (строка 2, колонка 1) позволяет менять порядок колонок/строк на заполненной таблице без необходимости каждый раз
    менять данные о позиции ячеек

    Использование:
        table = TableProxy(Znanie.objects.get(id=1))
        Выкидывает KnowledgeProxyError в случае ошибки

        Используется в двух местах:
        1) при рендере Таблицы (тег render_knowledge)
            get_render_data()
                возвращает заголовки таблицы и значения ячеек в виде матрицы rows x cols (так проще выполнять рендер)
                со значением либо текст, либо Знание

        2) При редактировании Таблицы в конструкторе Таблицы
            get_header_and_cells()
                возвращает заголовки и ячейки в виде словаря
                {"row:col" : {"id": knowledge.id или 0, "text": text или knowledge.name}}

            update_table(self, new_table_data: dict, user: User):
                обновляет таблицу из словаря new_table_data, который по структуре похож на метаданные,
                только поле 'cells' в виде словаря {"row:col" : {"id": knowledge.id или 0, "text": text или knowledge.name}}
    """

    table_key = "table"  # ключ для структуры таблицы
    cell_relation = "Состав"
    cell_key = "cell"  # ключ для позиции ячейки

    def __init__(self, knowledge: Znanie):
        if knowledge.tz != Tz.t_("Таблица"):
            raise KnowledgeProxyError(f"{knowledge} не таблица")

        self.knowledge = knowledge

    def _get_data(self, key):
        return self.knowledge.get_meta_info(key)

    def _set_data(self, key, data):
        self.knowledge.set_meta_info(key, data)

    @staticmethod
    def get_cell_data(cell: Relation):
        """возвращает row_id и col_id для ячейки"""

        meta_info = cell.get_meta_info(TableProxy.cell_key)
        if not meta_info:
            raise KnowledgeProxyError(f"Не удалось получить метаинформацию для ячейки {cell}")

        row_id = meta_info["row"]
        col_id = meta_info["col"]
        return row_id, col_id

    def is_zero_table(self):
        """
        проверка на нулевую таблицу
        нулевая таблица - если нет данных о структуре таблицы
        либо колонки и/или строки не установлены
        """
        header = self._get_data(self.table_key)
        if not header:
            return True

        if not header.get("rows") or not header.get("cols"):
            return True

        return False

    def is_empty_table(self):
        """
        Проверка на пустую (не заполненную) таблицу
        """
        return not bool(self.get_cells(in_list=True))

    def get_header(self, remove_cells=False):
        """
        Возвращает словарь со структурой таблицы
        {
        'version': 3, # версия структуры таблицы
        'group': 'Заголовок верхний левый угол таблицы',
        'group_row': 'Заголовок строк',
        'group_col': 'Заголовок колонок',
        'cols': [{'id':12, 'name: 'колонка 1'}],
        'rows': [{'id':10, 'name: 'Строка 1'}],
        'cells' : {'row_id:col_id': {'state':1, 'value': 'текст в ячейке', 'user_id': 'идентификатор пользователя'}},
        }
        """
        header = self._get_data(self.table_key)
        # возвращаем пустую структуру, если нет данных
        if not header:
            header = {
                "version": CURRENT_TABLE_VERSION,
                "group": "",
                "group_row": "",
                "group_col": "",
                "cols": [],
                "rows": [],
            }
        # версия структуры таблицы по умолчанию = 1 (самая первая)
        header.setdefault("version", 1)

        # удаляем словарь cells из заголовка
        if remove_cells and 'cells' in header:
            header.pop('cells')

        return header

    def get_render_data(self):
        """ Возвращает данные для рендера таблицы
            Заголовки и матрицу ячеек
        """
        header = self.get_header(remove_cells=True)
        values = self.get_cells(in_list=False)

        return header, values

    def extract_header_cells(self, header) -> dict:
        """
           Извлекаем ячейки из заголовка - в зависимости от формата хранения
           возвращает словарь с данными о ячейках в последнем действующем формате
        """
        header_cells = header.get("cells", {})
        # получаем данные о ячейках
        # раньше в cells хранился словарь {"row:col" : "text"}
        # теперь - {"row:col" : {"user_id": id, "value": 'text'}}
        # если по ключу "value" значения нет, берем все значение (для совместимости со старым форматом)
        # UPD теперь - {"row:col" : {"state":1, "user_id": id, "value": 'text'}}
        cells = {}

        # владелец табличного знания. Если пользователь не указан - значит владелец он
        owner_id = self.knowledge.user_id

        for key, value in header_cells.items():
            if header["version"] > 1 and not isinstance(value, dict):
                raise KnowledgeProxyError(f"Неверный формат данных в ячейке {key}: {value}")

            text = value.get("value", value) if hasattr(value, "get") else value
            user_id = value.get("user_id", owner_id) if hasattr(value, "get") else owner_id
            state = value.get("state", 0) if hasattr(value, "get") else 0

            cells[key] = {"value": text, "user_id": user_id, "state": state}
        return cells

    def get_cells(self, in_list=True):
        """
        если in_list=True
        получаем данные о ячейках - возвращает словарь
        {'row:col': {'id': id, 'text': text}, ...}

        если in_list=False
        возвращает матрицу row x col со значениями ячеек
        knowledge или None (если ячейка пустая)
        """
        header = self.get_header()
        cells = self.extract_header_cells(header)
        relation_cells = self.knowledge.base.filter(tr=Tr.t_(self.cell_relation)).select_related("rz")

        rows = {row["id"]: i for i, row in enumerate(header["rows"])}
        cols = {col["id"]: i for i, col in enumerate(header["cols"])}

        for cell in relation_cells:
            row_id, col_id = self.get_cell_data(cell)

            # проверяем, что ячейка существует
            # она может не существовать - если данные неконсистентны
            if row_id in rows and col_id in cols:
                key = f'{row_id}:{col_id}'

                # если ячейка уже забита текстом из заголовка таблицы - пропускаем
                # спорный вопрос - что в этом случае приоритетнее
                if key in cells:
                    # если ячейка уже забита текстом - пропускаем
                    if cells[key].get("value", None):
                        pass
                    else:
                        # если ячейка без текста - дополняем ее данными из базы
                        cells[key]["value"] = cell.rz.name
                        cells[key]["knowledge"] = cell.rz
                        cells[key]["id"] = cell.rz.pk

                else:
                    # добавляем данные в общий словарь значений ячеек
                    cells[key] = {"id": cell.rz.pk,
                                  "knowledge": cell.rz,
                                  "value": cell.rz.name,
                                  "user_id": cell.user_id,
                                  "state": 0,
                                  }

        if in_list:
            # удаляем ячейку с объектом Знание - она не нужна в этом формате
            # Этот словарь потом пойдет в редактор (в JSON)
            json_result = {key: {"id": value.get("id", 0),
                                 "text": value["value"],
                                 "user_id": value["user_id"],
                                 "state": value.get("state", 0)}
                           for key, value in cells.items()}
            return json_result

        # создаем матрицу таблицы для рендера.
        # В ячейке либо объект Знание, либо текст
        # Если ячейка пустая - в ячейке будет None
        matrix = [[None] * len(cols) for _ in range(len(rows))]
        for key, value in cells.items():
            row, col = map(int, key.split(":"))
            matrix[rows[row]][cols[col]] = value.get("knowledge", None) or value["value"]

        return matrix

    def get_header_and_cells(self):
        """
        Возвращает заголовок и список ячеек для формы заполнения
        """
        header = self.get_header(remove_cells=True)
        cells = self.get_cells(in_list=True)
        return header, cells

    def update_relations(self, new_cells: dict, user: User, update_owner=False):
        """ Обновляет связи с таблицей"""

        # получаем все текущие ячейки
        cells = self.knowledge.base.filter(tr=Tr.t_(self.cell_relation)).select_related("rz")
        author = Author.get_author_by_user(user)

        # получаем словарь старых ячеек
        old_cells = {}
        for cell in cells:
            row_id, col_id = self.get_cell_data(cell)
            old_cells[(row_id, col_id)] = cell

        # удаляем ячейки, которых нет в новом составе
        for_delete_cells = old_cells.keys() - new_cells.keys()

        # добавляем те ячейки, которых нет в старом составе
        for_add_cells = new_cells.keys() - old_cells.keys()

        # ячейки, которые есть в обоих наборах - надо возможно обновить.
        for_update_cells = old_cells.keys() & new_cells.keys()

        for cell in for_delete_cells:
            old_cells[cell].delete()

        for cell in for_update_cells:
            old_pk = int(old_cells[cell].rz.pk)
            new_pk = new_cells[cell]
            update_fields = []

            # если pk изменился - меняем запись
            if old_pk != new_pk:
                old_cells[cell].rz = Znanie.objects.get(pk=new_pk)
                update_fields.append("rz")

            # если проверяем создателя
            if update_owner:
                # если не совпадает user - меняем запись
                if old_cells[cell].user != user:
                    old_cells[cell].user = user
                    update_fields.append("user")

                # если не совпадает author - меняем запись
                if old_cells[cell].author != author:
                    old_cells[cell].author = author
                    update_fields.append("author")

            # если есть изменения - сохраняем
            if update_fields:
                old_cells[cell].save(update_fields=update_fields)

        for cell in for_add_cells:
            # добавляем новую ячейку
            cell_knowledge = Znanie.objects.get(pk=new_cells[cell])
            meta_info = json.dumps({"cell": {"row": cell[0], "col": cell[1]}})

            self.knowledge.base.create(
                tr=Tr.t_(self.cell_relation),
                rz=cell_knowledge,
                author=author,
                user=user,
                meta_info=meta_info,
            )

    @staticmethod
    def _has_repeats(data: dict):
        # возвращает True если в словаре есть повторяющиеся значения
        counter = Counter([int(item) for item in data.values() if item])
        result = [item for item in counter if counter[item] > 1]
        return bool(result)

    def check_can_update(self, new_header: dict,
                         new_data_cells: dict, new_header_cells: dict, user: User):
        """
        Проверяет права пользователя на возможность обновления таблицы.
        Выбрасывает исключения если нет такой возможности
        """

        # так как установлено требование уникальности для связи -
        # нельзя привязать больше одного раза знание к таблице
        if self._has_repeats(new_data_cells):
            raise KnowledgeProxyError("Значения в таблице повторяются!")

    def update_header(self, new_header: dict, new_cells: dict, user: User):
        """
        Обновляет заголовок таблицы
        и устанавливает новые значения и заменяет значения и пользователя-владельца
        считаем что проверка на возможность обновления уже проведена
        """
        old_header = self.get_header()
        old_cells = self.extract_header_cells(old_header)
        # решаем кто автор текста
        for key, value in new_cells.items():
            # ячейка есть такая и значение не поменялось
            if (key in old_cells) and (old_cells[key]["value"] != value["value"]):
                # значения не поменялись - оставляем авторство старое
                value["user_id"] = old_cells[key]["user_id"]
            else:
                value["user_id"] = user.pk

        new_header['cells'] = new_cells
        self._set_data(self.table_key, new_header)
        self.knowledge.save()

    def update_table(self, new_table_data: dict, user: User):
        """
        Обновляет таблицу в соответствии с новыми данными
        """

        def split_table_data(table_data):
            """
            Разделяет полученные данные на те, что хранятся в Связях и те, что хранятся в метаданных (текст)
            """
            _header = {
                'version': CURRENT_TABLE_VERSION,
                'group': table_data.get("group", ""),
                'group_row': table_data.get("group_row", ""),
                'group_col': table_data.get("group_col", ""),
                'cols': table_data.get("cols", []),
                'rows': table_data.get("rows", []),
            }
            cells = table_data.get("cells", {})

            _header_cells = {}
            _data_cells = {}

            # разделяем данные на те, что хранятся в Связях и те, что хранятся в метаданных (текст)
            for key, value in cells.items():
                row, col = key.split(':')
                # значит это знание в ячейке
                if 'state' in value:
                    _header_cells[key] = {'state': value['state']}

                if value['id']:
                    _data_cells[(int(row), int(col))] = value['id']

                else:
                    _header_cells.setdefault(key, {})['value'] = value['text']

            return _header, _header_cells, _data_cells

        header, header_cells, data_cells = split_table_data(new_table_data)

        self.check_can_update(header, data_cells, header_cells, user)

        # надо бы все в транзакцию заключить????
        self.update_header(header, header_cells, user)
        self.update_relations(data_cells, user)
