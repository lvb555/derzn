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

            def create_relation(tr__name, rz__id, bz__id):
                relation = Relation()
                try:
                    Relation.objects.get(tr__name=tr__name, bz__id=bz__id,
                                         rz__id=rz__id)
                except Relation.DoesNotExist:
                    relation.bz = Znanie.objects.get(pk=bz__id)
                    relation.tr = Tr.objects.get(name=tr__name)
                    relation.rz = Znanie.objects.get(pk=rz__id)
                    relation.author = Author.objects.get(name='Тест')
                    relation.is_published = True
                    relation.user_id = request.user.id
                    relation.save()

            # Создание связи "Строка": базовое знание - знание, связанное знание - строка
            create_relation('Строка', selected_row_pk, selected_znanie_pk)

            # Создание связи "Столбец": базовое знание - знание, связанное знание - столбец
            create_relation('Столбец', selected_column_pk, selected_znanie_pk)

            # Создание связи "Значение" : базовое знание - таблица, связанное знание - знание
            create_relation('Значение', selected_znanie_pk, selected_table_pk)

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

    # Выбор опубликованных знаний вида "Таблица" в пределах компетенции эксперта
    table_dict = {}
    for category in categories:
        zn_in_this_category = zn_list.filter(category=category).order_by('name')

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
    new_znanie = Znanie.objects.all().order_by('-id')[0]
    return JsonResponse([new_znanie.id, new_znanie.name], safe=False)

