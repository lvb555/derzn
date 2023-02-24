from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from drevo.models.author import Author
from drevo.models.knowledge import Znanie
from drevo.models.knowledge_kind import Tz
from drevo.models.relation_type import Tr
from drevo.models.relation import Relation
from drevo.models.special_permissions import SpecialPermissions

from .my_interview_view import search_node_categories

import json
import re


def filling_tables(request):
    """
    Отображение страницы "Ввод табличных значений"
    """
    expert = get_object_or_404(SpecialPermissions, expert=request.user)

    if expert:

        # Нахождение id связей с именами "Строка", "Столбец" и "Значение"
        row_id = Tr.objects.get(name='Строка').id
        column_id = Tr.objects.get(name='Столбец').id

        context = get_contex_data(expert, row_id, column_id)
        template_name = "drevo/filling_tables.html"

        if context != {}:
            return render(request, template_name, context)

    return HttpResponseRedirect(reverse('drevo'))


def get_contex_data(obj, row_id, column_id):
    """
    Получение всех таблиц, удовлетворяющих условию, а также атрибутов для создания знания
    """
    context = {}
    categories_expert = obj.categories.all()

    # Получаем список категорий по уровням
    categories = search_node_categories(categories_expert)
    tz_id = Tz.objects.get(name="Таблица").id
    zn_queryset = Znanie.objects.filter(tz_id=tz_id, is_published=True)

    # Выбор опубликованных знаний вида "Таблица" в пределах компетенции эксперта
    table_dict = {}
    for category in categories:
        zn_in_this_category = zn_queryset.filter(category=category).order_by('name')

        for zn in zn_in_this_category:
            table_dict[zn.pk] = zn.name

    # Список всех опубликованных несистемных знаний
    non_systemic_kind = Znanie.objects.filter(tz__is_systemic=False)
    zn = non_systemic_kind.values('id', 'name').order_by('name')

    context["table_dict"] = table_dict
    context["znanie"] = zn

    # Проверка, существует ли хотя бы строка и столбец хотя бы в одной подходящей таблице
    for table, table_id in enumerate(table_dict):
        if Relation.objects.filter(tr_id=row_id, bz_id=table_id, is_published=True).exists() and Relation.objects.filter(
                tr_id=column_id, bz_id=table_id, is_published=True).exists():
            return context

    return {}


def get_rows_and_columns(request):
    """
    Возвращает атрибуты строк и столбцов, связанных с данной таблицей: id и имя каждого знания
    """
    data = json.loads(request.body)
    table_id = data['id']

    # Получение id и имени знаний, связанных с таблицей с помощью вида "Строка"
    selected_rows = Relation.objects.filter(tr__name="Строка", bz_id=table_id)
    rows_name = selected_rows.values('rz_id', 'rz__name').order_by('-rz__order')

    # Получение id и имени знаний, связанных с таблицей с помощью вида "Столбец"
    selected_columns = Relation.objects.filter(tr__name="Столбец", bz_id=table_id)
    columns_name = selected_columns.values('rz_id', 'rz__name').order_by('-rz__order')

    return JsonResponse([list(rows_name), list(columns_name)], safe=False)


def znanie_attributes(request):
    """
    Возвращает атрибуты выбранного знания: вид знания, автор, содержимое
    """
    data = json.loads(request.body)
    znanie_id = data['id']
    current_zn = Znanie.objects.get(pk=znanie_id)

    knowledge_kind = current_zn.tz

    author_name = current_zn.author.name if current_zn.author else "Нет автора"

    # Удаление тегов HTML в тексте ячейки
    content = re.sub(r"<[^>]+>", " ", current_zn.content, flags=re.S)
    if not content:
        return JsonResponse([knowledge_kind.name, author_name], safe=False)
    return JsonResponse([knowledge_kind.name, author_name, content], safe=False)


def show_new_znanie(request):
    """
    Возвращает id и имя последнего созданного знания
    """
    new_znanie = Znanie.objects.all().order_by('-id')[0]
    return JsonResponse([new_znanie.id, new_znanie.name], safe=False)


def show_filling_tables_page(request):
    """Возвращает True для показа страницы «Наполнение таблиц», если существует хотя бы одна таблица в компетенции
    эксперта и в ней есть хотя бы одна строка и столбец"""

    expert = SpecialPermissions.objects.filter(expert=request.user)

    if expert.exists():
        row_id = Tr.objects.get(name='Строка').id
        column_id = Tr.objects.get(name='Столбец').id
        context = get_contex_data(expert.first(), row_id, column_id)
        if context != {}:
            data = True
        else:
            data = False
    return JsonResponse([data], safe=False)


def get_form_data(request):
    """
    Создание трех связей таблицы, строки, столбца и значения при условии, что заполнены все поля
    """

    # Нахождение id связей с именами "Строка" и "Столбец"
    row_id = Tr.objects.get(name='Строка').id
    column_id = Tr.objects.get(name='Столбец').id
    value_id = Tr.objects.get(name='Значение').id

    # Получение значений выбранной таблицы, знания, строки и столбца
    selected_table_pk = request.POST.get('table')
    selected_znanie_pk = request.POST.get('znanie')
    selected_row_pk = request.POST.get('row')
    selected_column_pk = request.POST.get('column')

    def create_relation(tr_id, rz_id, bz_id):
        """Создание опубликованной связи с заданными параметрами"""

        # Создание автора с именем и фамилией пользователя, если такого не существует
        author, created = Author.objects.get_or_create(
            name=f"{request.user.first_name} {request.user.last_name}",
        )

        # Создание или нахождение опубликованной связи с выбранными значениями
        Relation.objects.get_or_create(
            tr_id=tr_id,
            bz_id=bz_id,
            rz_id=rz_id,
            author_id=author.id,
            user_id=request.user.id,
            is_published=True
        )

    # Создание связи "Строка": базовое знание - знание, связанное знание - строка
    create_relation(row_id, selected_row_pk, selected_znanie_pk)

    # Создание связи "Столбец": базовое знание - знание, связанное знание - столбец
    create_relation(column_id, selected_column_pk, selected_znanie_pk)

    # Создание связи "Значение" : базовое знание - таблица, связанное знание - знание
    create_relation(value_id, selected_znanie_pk, selected_table_pk)

    return HttpResponse('Данные были успешно сохранены')

