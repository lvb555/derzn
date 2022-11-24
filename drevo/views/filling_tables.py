from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect, render

from drevo.models.author import Author
from drevo.models.category import Category
from drevo.models.knowledge import Znanie
from drevo.models.knowledge_kind import Tz
from drevo.models.relation_type import Tr
from drevo.models.relation import Relation

import json
import re


def filling_tables(request):
    """
    Отображение страницы "Ввод табличных значений", сохранение данных в форму
    """

    expert = request.user.expert.all()

    if expert:
        context = get_contex_data(expert[0])

        template_name = "drevo/filling_tables.html"

        if request.method == 'POST':
            selected_table_pk = request.POST.get('table')
            selected_znanie_pk = request.POST.get('znanie')
            selected_row_pk = request.POST.get('row')
            selected_column_pk = request.POST.get('column')

            # Создание связи "Значение" : базовое знание - таблица, связанное знание - знание
            znanie_and_table = Relation()
            try:
                Relation.objects.get(tr__name='Значение', bz__id=selected_table_pk,
                                     rz__id=selected_znanie_pk)
            except Relation.DoesNotExist:
                znanie_and_table.bz = Znanie.objects.get(pk=selected_table_pk)
                znanie_and_table.tr = Tr.objects.get(name='Значение')
                znanie_and_table.rz = Znanie.objects.get(pk=selected_znanie_pk)
                znanie_and_table.author = Author.objects.get(name='Я')
                znanie_and_table.is_published = True
                znanie_and_table.user_id = request.user.id
                znanie_and_table.save()

            # Создание связи "Строка": базовое знание - знание, связанное знание - строка
            znanie_and_row = Relation()
            try:
                Relation.objects.get(tr__name='Строка', bz__id=selected_znanie_pk,
                                     rz__id=selected_row_pk)
            except Relation.DoesNotExist:
                znanie_and_row.bz = Znanie.objects.get(pk=selected_znanie_pk)
                znanie_and_row.tr = Tr.objects.get(name='Строка')
                znanie_and_row.rz = Znanie.objects.get(pk=selected_row_pk)
                znanie_and_row.author = Author.objects.get(name='Я')
                znanie_and_row.is_published = True
                znanie_and_row.user_id = request.user.id
                znanie_and_row.save()

            # Создание связи "Столбец": базовое знание - знание, связанное знание - столбец
            znanie_and_column = Relation()
            try:
                Relation.objects.get(tr__name='Столбец', bz__id=selected_znanie_pk,
                                     rz__id=selected_column_pk)
            except Relation.DoesNotExist:
                znanie_and_column.bz = Znanie.objects.get(pk=selected_znanie_pk)
                znanie_and_column.tr = Tr.objects.get(name='Столбец')
                znanie_and_column.rz = Znanie.objects.get(pk=selected_column_pk)
                znanie_and_column.author = Author.objects.get(name='Я')
                znanie_and_column.is_published = True
                znanie_and_column.user_id = request.user.id
                znanie_and_column.save()

            return HttpResponse("Данные были успешно сохранены!")

        return render(request, template_name, context)

    return redirect("/drevo/")


def search_node_categories(categories_expert):
    """
    Выбор категорий, реализация как в файле my_interview_view.py
    """
    list_category_id = []
    for category_expert in categories_expert:
        list_level = Category.objects.filter(tree_id=category_expert.tree_id)
        for category_child in list_level[category_expert.level :]:
            if category_expert.level > category_child.level:
                continue
            elif category_expert.level >= category_child.level:
                list_category_id.append(category_expert.id)
            else:
                list_category_id.append(category_child.id)
    list_category_id = list(set(list_category_id))
    categories = Category.tree_objects.filter(
        is_published=True, id__in=list_category_id
    )
    return categories


def get_contex_data(obj):
    """
    Получение всех таблиц, удовлетворяющих условию, а также атрибутов для создания знания
    """
    context = {}
    categories_expert = obj.categories.all()

    # Получаем список категорий по уровням
    categories = search_node_categories(categories_expert)
    tz_id = Tz.objects.get(name="Таблица").id
    zn_list = Znanie.objects.filter(tz_id=tz_id, is_published=True)

    table_dict = {}
    znanie_dict = {}

    # Выбор опубликованных знаний вида "Таблица" в пределах компетенции эксперта
    for category in categories:
        zn_in_this_category = zn_list.filter(category=category)
        for zn in zn_in_this_category:
            table_dict[zn.pk] = zn.name

    # Сортировка по алфавиту
    table_dict = dict(sorted(table_dict.items(), key=lambda item: item[1]))

    # Список всех опубликованных несистемных знаний
    non_systemic_kind = Tz.objects.filter(is_systemic=False)
    for objects in non_systemic_kind:
        non_systemic_published = Znanie.objects.filter(tz_id=objects.id, is_published=True)
        for znanie in non_systemic_published:
            znanie_dict[znanie.pk] = znanie.name

    # Сортировка по алфавиту
    znanie_dict = dict(sorted(znanie_dict.items(), key=lambda item: item[1]))

    context["table_dict"] = table_dict
    context["znanie_dict"] = znanie_dict

    return context


def get_rows_and_columns(request):
    """
    Выбор связанных с данной таблицей строк и столбцов
    """
    data = json.loads(request.body)
    table_id = data['id']

    # Получение id и имени знаний, связанных с таблицей с помощью вида "Строка"
    row_relation = Tr.objects.get(name="Строка").id
    selected_rows = Relation.objects.filter(tr_id=row_relation, bz_id=table_id)
    rows_name = {}
    for s in selected_rows:
        rows_name[s.rz.id] = s.rz.name
    rows_name = dict(sorted(rows_name.items(), key=lambda item: item[1]))

    # Получение id и имени знаний, связанных с таблицей с помощью вида "Столбец"
    column_relation = Tr.objects.get(name="Столбец").id
    selected_columns = Relation.objects.filter(tr_id=column_relation, bz_id=table_id)
    columns_name = {}
    for s in selected_columns:
        columns_name[s.rz.id] = s.rz.name
    columns_name = dict(sorted(columns_name.items(), key=lambda item: item[1]))
    return JsonResponse([rows_name, columns_name], safe=False)


def znanie_attributes(request):
    """
    Атрибуты выбранного знания: вид знания, автор, содержимое
    """
    data = json.loads(request.body)
    znanie_id = data['id']
    current_zn = Znanie.objects.get(pk=znanie_id)

    if current_zn.author:
        author = Author.objects.get(name=current_zn.author)
        author_name = author.name
    else:
        author_name = "Нет автора"

    knowledge_kind = Tz.objects.get(name=current_zn.tz)

    # Удаление тегов HTML в тексте ячейки
    content = re.sub(r"<[^>]+>", " ", current_zn.content, flags=re.S)
    if not content:
        return JsonResponse([knowledge_kind.name, author_name], safe=False)

    return JsonResponse([knowledge_kind.name, author_name, content], safe=False)
