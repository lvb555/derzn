from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.generic import TemplateView

from drevo.models.author import Author
from drevo.models.knowledge import Znanie
from drevo.models.knowledge_kind import Tz
from drevo.models.relation_type import Tr
from drevo.models.relation import Relation
from drevo.models.special_permissions import SpecialPermissions

from .knowledge_tp_view import get_knowledge_dict
from .my_interview_view import search_node_categories

import json
import re


class TableKnowledgeTreeView(LoginRequiredMixin, TemplateView):
    """
    Представление страницы дерева табличных знаний
    """
    template_name = 'drevo/table_create_and_update.html'

    def get_context_data(self, **kwargs):
        """Передает контекст в шаблон"""
        context = super().get_context_data(**kwargs)
        user = self.request.user
        # Формирование списка знаний вида "Таблица" со статусом "Опубликованное знание"
        zn = Znanie.objects.filter(
            Q(tz__name='Таблица') & Q(knowledge_status__status='PUB')
        )

        for z in zn:
            row_id = get_object_or_404(Tr, name='Строка').id
            column_id = get_object_or_404(Tr, name='Столбец').id
            # Проверка, существуют ли в таблице опубликованные строка и столбец
            if not(Relation.objects.filter(tr_id=row_id, bz_id=z.id, is_published=True).exists() and
                   Relation.objects.filter(tr_id=column_id, bz_id=z.id, is_published=True).exists()):
                zn = zn.exclude(id=z.id)

        context['ztypes'], context['zn_dict'] = get_knowledge_dict(zn, user=user)
        context['title'] = 'Дерево табличных знаний'

        return context


class CreateChangeTableView(LoginRequiredMixin, TemplateView):
    """
    Представление страницы создания/изменения таблиц
    """
    template_name = 'drevo/table_create_and_update.html'

    def get_context_data(self, **kwargs):
        """Передает контекст в шаблон"""
        context = super().get_context_data(**kwargs)
        user = self.request.user
        # Формирование списка знаний вида "Таблица" со статусом "Опубликованное знание"
        zn = Znanie.objects.filter(
            Q(tz__name='Таблица') & Q(knowledge_status__status='PUB')
        )
        context['ztypes'], context['zn_dict'] = get_knowledge_dict(zn, user=user)
        context['title'] = 'Создание и изменение таблиц'
        context['table_create'] = True

        return context


def filling_tables(request, pk):
    """
    Отображение страницы "Ввод табличных значений"
    """
    expert = get_object_or_404(SpecialPermissions, expert=request.user)

    if expert:
        context = get_contex_data(pk)
        template_name = "drevo/filling_tables.html"
        return render(request, template_name, context)

    return HttpResponseRedirect(reverse('drevo'))


def table_constructor(request, pk):
    """
    Отображение страницы "Конструктор таблиц"
    """
    expert = get_object_or_404(SpecialPermissions, expert=request.user)

    if expert:

        context = get_contex_data(pk, table_create=True)
        template_name = "drevo/table_constructor.html"
        return render(request, template_name, context)

    return HttpResponseRedirect(reverse('drevo'))


def get_contex_data(pk, table_create=False):
    """
    Получение выбранной таблицы, связанных с ней строк и столбцов, а также несистемных знаний
    в случае работы со страницей "Наполнение таблиц"
    """
    context = {}

    if pk == '0':
        return context
    selected_table = Znanie.objects.get(id=pk)
    table_attributes = {selected_table.id: selected_table.name}
    table_id = pk

    # Получение id и имени знаний, связанных с таблицей с помощью вида "Строка"
    selected_rows = Relation.objects.filter(tr__name="Строка", bz_id=table_id)
    rows_attributes = selected_rows.values('rz_id', 'rz__name').order_by('-rz__order')

    # Получение id и имени знаний, связанных с таблицей с помощью вида "Столбец"
    selected_columns = Relation.objects.filter(tr__name="Столбец", bz_id=table_id)
    columns_attributes = selected_columns.values('rz_id', 'rz__name').order_by('-rz__order')

    if not table_create:
        # Список всех опубликованных несистемных знаний в случае открытия страницы "Наполнение таблиц"
        non_systemic_kind = Znanie.objects.filter(tz__is_systemic=False)
        zn = non_systemic_kind.values('id', 'name').order_by('name')
        context["znanie"] = zn

    context["table_dict"] = table_attributes
    context["rows_attributes"] = rows_attributes
    context["columns_attributes"] = columns_attributes

    return context


def show_filling_tables_page(request):
    """Возвращает True для показа страницы «Наполнение таблиц», если существует хотя бы одна таблица в компетенции
    эксперта и в ней есть хотя бы одна строка и столбец"""

    expert = SpecialPermissions.objects.filter(expert=request.user)

    if expert.exists():
        categories_expert = object.categories.all()
        row_id = get_object_or_404(Tr, name='Строка').id
        column_id = get_object_or_404(Tr, name='Столбец').id
        categories = search_node_categories(categories_expert)
        tz_id = get_object_or_404(Tz, name="Таблица").id
        zn_queryset = Znanie.objects.filter(tz_id=tz_id, is_published=True)

        # Выбор опубликованных знаний вида "Таблица" в пределах компетенции эксперта
        table_dict = {}
        for category in categories:
            zn_in_this_category = zn_queryset.filter(category=category).order_by('name')

            for zn in zn_in_this_category:
                table_dict[zn.pk] = zn.name

        data = False
        for table, table_id in enumerate(table_dict):
            if Relation.objects.filter(tr_id=row_id, bz_id=table_id,
                                       is_published=True).exists() and Relation.objects.filter(
                    tr_id=column_id, bz_id=table_id, is_published=True).exists():
                data = True

    return JsonResponse([data], safe=False)


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


def get_form_data(request):
    """
    Создание трех связей таблицы, строки, столбца и значения при условии, что заполнены все поля
    """

    # Нахождение id связей с именами "Строка" и "Столбец"
    row_id = get_object_or_404(Tr, name='Строка').id
    column_id = get_object_or_404(Tr, name='Столбец').id
    value_id = get_object_or_404(Tr, name='Значение').id

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
            is_published=True,
            defaults={'user_id': request.user.id}
        )

    # Создание связи "Строка": базовое знание - знание, связанное знание - строка
    create_relation(row_id, selected_row_pk, selected_znanie_pk)

    # Создание связи "Столбец": базовое знание - знание, связанное знание - столбец
    create_relation(column_id, selected_column_pk, selected_znanie_pk)

    # Создание связи "Значение" : базовое знание - таблица, связанное знание - знание
    create_relation(value_id, selected_znanie_pk, selected_table_pk)

    return HttpResponse('Данные были успешно сохранены')

