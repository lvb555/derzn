from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.urls import reverse

from drevo.models.author import Author
from drevo.models.category import Category
from drevo.models.knowledge import Znanie
from drevo.models.knowledge_kind import Tz
from drevo.models.relation_type import Tr
from drevo.models.relation import Relation

from .my_interview_view import search_node_categories

import json
import re


def filling_tables(request):
    """
    Отображение страницы "Ввод табличных значений", сохранение данных в форму
    """
    expert = request.user.expert

    if expert:
        context = get_contex_data(expert)

        template_name = "drevo/filling_tables.html"

        if request.method == 'POST':
            # Получение значений выбранной таблицы, знания, строки и столбца
            selected_table_pk = request.POST.get('table')
            selected_znanie_pk = request.POST.get('znanie')
            selected_row_pk = request.POST.get('row')
            selected_column_pk = request.POST.get('column')

            # Проверка, все ли необходимые поля заполнены
            if not selected_table_pk or not selected_znanie_pk or not selected_row_pk or not selected_column_pk:
                return HttpResponse("Необходимо заполнить все поля для создания связей!")

            def create_relation(tr_id, rz_id, bz_id):
                """Создание опубликованной связи с заданными параметрами"""

                # Создание автора с именем и фамилией пользователя, если такого не существует
                author, created = Author.objects.get_or_create(
                    name=f"{request.user.first_name} {request.user.last_name}"
                )
                Relation.objects.get_or_create(
                    tr_id=tr_id,
                    bz_id=bz_id,
                    rz_id=rz_id,
                    author_id=author.id,
                    user_id=request.user.id,
                    is_published=True
                )

            # Нахождение id связей с именами "Строка", "Столбец" и "Значение"
            row_id = Tr.objects.get(name='Строка').id
            column_id = Tr.objects.get(name='Столбец').id
            value_id = Tr.objects.get(name='Значение').id

            # Создание связи "Строка": базовое знание - знание, связанное знание - строка
            create_relation(row_id, selected_row_pk, selected_znanie_pk)

            # Создание связи "Столбец": базовое знание - знание, связанное знание - столбец
            create_relation(column_id, selected_column_pk, selected_znanie_pk)

            # Создание связи "Значение" : базовое знание - таблица, связанное знание - знание
            create_relation(value_id, selected_znanie_pk, selected_table_pk)

            return HttpResponse("Данные были успешно сохранены!")

        return render(request, template_name, context)

    return reverse("/drevo/")


def get_contex_data(obj):
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

    return context


def get_rows_and_columns(request):
    """
    Выбор связанных с данной таблицей строк и столбцов
    """
    data = json.loads(request.body)
    table_id = data['id']

    # Получение id и имени знаний, связанных с таблицей с помощью вида "Строка"
    selected_rows = Relation.objects.filter(tr__name="Строка", bz_id=table_id)
    rows_name = selected_rows.values('rz_id', 'rz__name').order_by('rz__name')

    # Получение id и имени знаний, связанных с таблицей с помощью вида "Столбец"
    selected_columns = Relation.objects.filter(tr__name="Столбец", bz_id=table_id)
    columns_name = selected_columns.values('rz_id', 'rz__name').order_by('rz__name')

    return JsonResponse([list(rows_name), list(columns_name)], safe=False)


def znanie_attributes(request):
    """
    Атрибуты выбранного знания: вид знания, автор, содержимое
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
    Показывает только что созданное знание, обращается после нажатия на кнопку "Сохранить" к базе данных
    и вытаскивает атрибуты последней записи
    """
    new_znanie = Znanie.objects.all().order_by('-id')[0]
    return JsonResponse([new_znanie.id, new_znanie.name], safe=False)
