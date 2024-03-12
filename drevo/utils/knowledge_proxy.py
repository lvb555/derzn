"""
Объекты - обертки для знаний, представляющие дополнительный функционал
"""
import json

from drevo.models import Znanie, Tz, Tr, Relation, Author
from users.models import User


class KnowledgeProxyError(Exception):
    pass


class TableProxy:
    """
    Для упрощения работы с таблицами
    """

    table_key = 'table'  # ключ для структуры таблицы
    cell_relation = 'Состав'
    cell_key = 'cell'  # ключ для позиции ячейки

    def __init__(self, knowledge: Znanie):
        if knowledge.tz != Tz.t_('Таблица'):
            raise KnowledgeProxyError(f'{knowledge} не таблица')

        self.knowledge = knowledge

        data = self.knowledge.meta_info
        if not data:
            self.meta_info = {}

        else:
            self.meta_info = json.loads(self.knowledge.meta_info)

    def _save(self):
        self.knowledge.meta_info = json.dumps(self.meta_info, ensure_ascii=False)
        self.knowledge.save()

    def get_data(self, key):
        return self.meta_info.get(key, None)

    def set_data(self, key, data):
        self.meta_info[key] = data

    @staticmethod
    def set_ids(header_data):
        # устанавливаем идентификаторы для колонок и строк если они не установлены
        # логика такая - находим максимум id и нумеруем все по возрастанию где нет id (или он 0)

        # колонки
        max_id = 0
        cols_list = []
        for col in header_data['cols']:
            if not col.get('id'):
                cols_list.append(col)
            else:
                max_id = max(max_id, int(col['id']))

        for col in cols_list:
            max_id += 1
            col['id'] = max_id

        # строки
        max_id = 0
        rows_list = []
        for row in header_data['rows']:
            if not row.get('id'):
                rows_list.append(row)
            else:
                max_id = max(max_id, int(row['id']))

        for row in rows_list:
            max_id += 1
            row['id'] = max_id

    @staticmethod
    def get_cell_data(cell: Relation):
        """ возвращает row_id и col_id для ячейки """

        if cell.meta_info:
            meta_info = json.loads(cell.meta_info)
        else:
            raise ValueError(f'Не удалось получить метаинформацию для ячейки {cell}')

        row_id = meta_info['cell']['row']
        col_id = meta_info['cell']['col']
        return row_id, col_id

    @staticmethod
    def headers_is_eq(old_header: dict, new_header: dict):
        """
        сравнение двух словарей с данными о колонках и строках
        так как порядок колонок и строк в списке важен, а порядок ключей вроде бы всегда получается одинаковый
         (как из формы редактирования приходит) - будем тупо сравнивать по текстовому представлению
        """
        return str(old_header) == str(new_header)

    def is_zero_table(self):
        """
            проверка на нулевую таблицу
            нулевая таблица - если нет данных о структуре таблицы
            либо колонки и/или строки не установлены
        """
        header = self.get_data(self.table_key)
        if not header:
            return True

        if not header.get('rows') or not header.get('cols'):
            return True

        return False

    def update_header(self, header_data: dict):
        old_header_data = self.get_data(self.table_key)

        if self.headers_is_eq(old_header_data, header_data):
            # таблица не изменилась
            raise KnowledgeProxyError('Таблица не изменилась')

        if not old_header_data:
            # все просто - записываем данные
            self.set_ids(header_data)
            self.set_data(self.table_key, header_data)
            self._save()
            return

        # надо обновлять данные
        # ищем что удалили
        old_row_ids = set([row['id'] for row in old_header_data['rows']])
        old_col_ids = set([col['id'] for col in old_header_data['cols']])

        new_row_ids = set([row['id'] for row in header_data['rows'] if row['id']])
        new_col_ids = set([col['id'] for col in header_data['cols'] if col['id']])

        # ищем те колонки и столбцы, что были удалены
        rows_for_del = old_row_ids - new_row_ids
        cols_for_del = old_col_ids - new_col_ids

        records_for_delete = []
        cells = self.knowledge.base.filter(tr=Tr.t_(self.cell_relation)).select_related("rz")

        # получаем список ячеек которые надо удалить - потому что эти строки и колонки удалили
        for cell in cells:
            row_id, col_id = self.get_cell_data(cell)
            if (row_id in rows_for_del) and (col_id in cols_for_del):
                records_for_delete.append(cell)

        Relation.objects.filter(pk__in=[rec.pk for rec in records_for_delete]).delete()
        # и теперь сохраняем
        self.set_ids(header_data)
        self.set_data(self.table_key, header_data)
        self._save()

    def update_values(self, header_data: dict, cells_data: dict, user: User):
        db_header_data = self.get_data(self.table_key)

        if db_header_data != header_data:
            raise KnowledgeProxyError('Заголовок таблицы изменился')

        # получаем все текущие ячейки
        cells = self.knowledge.base.filter(tr=Tr.t_(self.cell_relation)).select_related("rz")

        # получаем словарь старых ячеек
        old_cells = {}
        for cell in cells:
            row_id, col_id = self.get_cell_data(cell)
            old_cells[(row_id, col_id)] = cell

        new_cells = {}
        rows = [row['id'] for row in db_header_data['rows']]
        cols = [col['id'] for col in db_header_data['cols']]

        # преобразуем позиции ячеек из относительных в идентификаторы
        for new_cell in cells_data:
            row_id, col_id = rows[new_cell['row']], cols[new_cell['col']]
            new_cells[(row_id, col_id)] = new_cell

        # удаляем ячейки, которых нет в новом составе
        for_delete_cells = old_cells.keys() - new_cells.keys()

        # добавляем те ячейки, которых нет в старом составе
        for_add_cells = new_cells.keys() - old_cells.keys()

        # ячейки, которые есть в обоих наборах - надо возможно обновить.
        for_update_cells = old_cells.keys() & new_cells.keys()

        for cell in for_update_cells:
            old_pk = int(old_cells[cell].rz.pk)
            new_pk = int(new_cells[cell]['id'])

            # если pk изменился - меняем запись
            if old_pk != new_pk:
                old_cells[cell].rz = Znanie.objects.get(pk=new_pk)
                old_cells[cell].save(update_fields=['rz'])

        for cell in for_delete_cells:
            old_cells[cell].delete()

        for cell in for_add_cells:
            # добавляем новую ячейку
            cell_knowledge = Znanie.objects.get(pk=new_cells[cell]['id'])
            meta_info = json.dumps({'cell': {'row': cell[0], 'col': cell[1]}})

            # создаем автора. Реально через фамилию и имя связь?????
            author, created = Author.objects.get_or_create(
                name=f"{user.first_name} {user.last_name}",
            )
            self.knowledge.base.create(tr=Tr.t_(self.cell_relation),
                                       rz=cell_knowledge,
                                       author=author,
                                       user=user,
                                       meta_info=meta_info)

    def get_header(self):
        header = self.get_data(self.table_key)
        if not header:
            header = {'group_row': '', 'group_col': '', 'cols': [], 'rows': []}

        return header

    def get_render_data(self):
        header = self.get_header()
        values = self.get_cells(in_list=False)
        return header, values

    def get_cells(self, in_list=True):
        """
        если in_list=True
        получаем данные о ячейках - возвращает список значений ячеек
        [{'row': row, 'col': col, 'knowledge': knowledge}, ...]

        если in_list=False
        возвращает матрицу row x col со значениями ячеек
        knowledge или None (если ячейка пустая)
        """
        header = self.get_header()

        cells = self.knowledge.base.filter(tr=Tr.t_(self.cell_relation)).select_related("rz")

        rows = {row['id']: i for i, row in enumerate(header['rows'])}
        cols = {col['id']: i for i, col in enumerate(header['cols'])}

        # получаем данные о ячейках
        table = []
        for cell in cells:
            row_id, col_id = self.get_cell_data(cell)

            if row_id in rows and col_id in cols:
                table.append({'row': rows[row_id], 'col': cols[col_id], 'knowledge': cell.rz})

        if in_list:
            return table

        matrix = [[None] * len(cols) for _ in range(len(rows))]

        for record in table:
            matrix[record['row']][record['col']] = record['knowledge']

        return matrix

    def get_header_and_cells(self):
        """
        Возвращает заголовок и список ячеек для формы заполнения
        """
        header = self.get_header()
        cells = self.get_cells(in_list=True)

        for cell in cells:
            cell['name'] = str(cell['knowledge'].name)
            cell['id'] = cell['knowledge'].pk
            del cell['knowledge']
        return header, cells
