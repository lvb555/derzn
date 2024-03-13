import json
from collections import Counter

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.forms import ModelChoiceField
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views.decorators.http import require_http_methods
from django.views.generic import (CreateView, DetailView, FormView,
                                  TemplateView, UpdateView)
from drevo.forms.constructor_knowledge_form import (
    MainZnInConstructorCreateEditForm, NameOfZnCreateUpdateForm,
    OrderOfRelationForm, ZnanieForCellCreateForm, ZnanieForRowOrColumnForm)
from drevo.forms.knowledge_create_form import ZnFilesFormSet, ZnImageFormSet
from drevo.models import Relation, SpecialPermissions, Tr, Tz, Znanie
from drevo.views.my_interview_view import search_node_categories

from ...utils.knowledge_proxy import KnowledgeProxyError, TableProxy
from .mixins import DispatchMixin
from .supplementary_functions import (create_relation,
                                      create_zn_for_constructor,
                                      get_file_from_request,
                                      get_images_from_request)

# --------------------------------------------------------------
# Views для конструктора таблиц и страницы "Наполнение таблицы"
# --------------------------------------------------------------


def show_filling_tables_page(request):
    """
    Страница «Наполнение таблиц» доступна, если существует хотя бы одна таблица в компетенции
    эксперта и в ней есть хотя бы одна строка и столбец.
    Используется, видимо только при построении меню в профиле - удаляет "Наполнение таблиц"
    """
    result = {"show": False}
    expert = get_object_or_404(SpecialPermissions, expert=request.user)

    if expert:
        categories_expert = expert.categories.all()
        categories = search_node_categories(categories_expert)

        expert_tables = Znanie.published.filter(
            category__in=categories, tz=Tz.t_("Таблица")
        )

        for table in expert_tables:
            if not TableProxy(table).is_zero_table():
                result["show"] = True
                break

    return JsonResponse(result, safe=False)


def get_contex_data(pk, type_of_page, user=None):
    """
    Получение данных для страниц "Наполнение таблиц", "Конструктор таблиц"
    """
    context = {}
    selected_table = get_object_or_404(Znanie, id=pk)
    table_id = pk

    group_kind = get_object_or_404(Tz, name="Группа").id
    structure_kind = get_object_or_404(Tr, name="Состав").id

    # Получение id и имени знаний, связанных с таблицей с помощью вида "Строка"
    selected_rows = Relation.objects.filter(tr__name="Строка", bz_id=table_id)
    rows_attributes = selected_rows.values("rz_id", "rz__name").order_by("-rz__order")

    # Получение id и имени знаний, связанных с таблицей с помощью вида "Столбец"
    selected_columns = Relation.objects.filter(tr__name="Столбец", bz_id=table_id)
    columns_attributes = selected_columns.values("rz_id", "rz__name").order_by(
        "-rz__order"
    )

    # Получение id и имени знаний, связанных со строкой с помощью вида "Состав"
    relation_row_group = Relation.objects.filter(
        bz_id=table_id, rz__tz_id=group_kind, tr__name="Строка", is_published=True
    ).first()
    if relation_row_group:
        row_group_structure = Relation.objects.filter(
            bz_id=relation_row_group.rz_id, tr_id=structure_kind
        )
        rows_structure_attributes = row_group_structure.values(
            "rz_id", "rz__name"
        ).order_by("-rz__order")
        context["rows_structure_attributes"] = rows_structure_attributes
        context["row_is_group"] = True

    # Получение id и имени знаний, связанных со столбцом с помощью вида "Состав"
    relation_column_group = Relation.objects.filter(
        bz_id=table_id, rz__tz_id=group_kind, tr__name="Столбец", is_published=True
    ).first()
    if relation_column_group:
        column_group_structure = Relation.objects.filter(
            bz_id=relation_column_group.rz_id, tr_id=structure_kind
        )
        columns_structure_attributes = column_group_structure.values(
            "rz_id", "rz__name"
        ).order_by("-rz__order")
        context["columns_structure_attributes"] = columns_structure_attributes
        context["column_is_group"] = True

    if type_of_page == "table_constructor":
        context["title"] = "Конструктор таблицы"
        context["type_of_zn"] = "table"
        # Формы для редактирования главного знания - таблицы
        main_zn_edit_form = MainZnInConstructorCreateEditForm(
            instance=selected_table, user=user, type_of_zn="table"
        )
        context["main_zn_edit_form"] = main_zn_edit_form
        context["main_zn_edit_form_uuid"] = main_zn_edit_form.fields[
            "content"
        ].widget.attrs["id"]
        context["images_form_for_main_zn"] = ZnImageFormSet(instance=selected_table)
        context["file_form_for_main_zn"] = ZnFilesFormSet(instance=selected_table)
        context["main_zn_name"] = f"Таблица: «{selected_table.name}»"
    elif type_of_page == "filling_tables":
        context["title"] = f"Наполнение таблицы «{selected_table.name}»"
        # Формы для создания знания в ячейке таблицы
        form = ZnanieForCellCreateForm(user=user)
        context["form"] = form
        context["zn_form_uuid"] = form.fields["content"].widget.attrs["id"]
        context["images_form"] = ZnImageFormSet()
        context["file_form"] = ZnFilesFormSet()

        # Список всех опубликованных несистемных знаний для ячейки таблицы
        non_systemic_zn = Znanie.objects.filter(
            tz__is_systemic=False, is_published=True
        )
        zn_attributes = non_systemic_zn.values("id", "name").order_by("name")
        context["non_systemic_zn"] = zn_attributes
        context["main_zn_name"] = selected_table.name

    context["main_zn_id"] = selected_table.id
    context["rows_attributes"] = rows_attributes
    context["columns_attributes"] = columns_attributes

    return context


class TableConstructorView(LoginRequiredMixin, DispatchMixin, TemplateView):
    """Представление для страницы «Конструктор таблиц»"""

    template_name = "drevo/constructors/table_constructor.html"

    def get_context_data(self, **kwargs):
        return get_contex_data(
            pk=self.kwargs.get("pk"),
            type_of_page="table_constructor",
            user=self.request.user,
        )


class FillingTablesView(LoginRequiredMixin, DispatchMixin, TemplateView):
    """Представление для страницы «Наполнение таблицы»"""

    template_name = "drevo/constructors/filling_tables.html"

    def get_context_data(self, **kwargs):
        return get_contex_data(
            pk=self.kwargs.get("pk"),
            type_of_page="filling_tables",
            user=self.request.user,
        )


@require_http_methods(["GET", "POST"])
def relation_in_table_create_update_view(request):
    tz_type_for_form = {
        "heading": NameOfZnCreateUpdateForm,
        "any_type": ZnanieForRowOrColumnForm,
    }
    if request.method == "GET":
        # Получение форм для создания знания
        if request.GET.get("action") == "create":
            zn_form = tz_type_for_form.get(request.GET.get("zn_tz_type"))()
            order_of_rel_form = OrderOfRelationForm()
        # Получение форм для редактирования знания
        else:
            current_zn = get_object_or_404(Znanie, id=request.GET.get("zn_id"))
            zn_form = ZnanieForRowOrColumnForm(instance=current_zn)
            order_of_relation = (
                Relation.objects.filter(rz_id=current_zn.id).first().order
            )
            order_of_rel_form = OrderOfRelationForm(
                initial={"order_of_relation": order_of_relation}
            )
        return JsonResponse(
            {
                "zn_form": f"{zn_form.as_p()}",
                "order_of_rel_form": f"{order_of_rel_form.as_p()}",
            }
        )
    else:
        # Сохранение нового/изменённого знания
        req_data = request.POST
        table_id = req_data.get("table_id")
        if req_data.get("action") == "edit":
            form = tz_type_for_form.get(req_data.get("zn_tz_type"))(
                data=req_data,
                instance=get_object_or_404(Znanie, id=req_data.get("edited_zn_id")),
            )
        else:
            form = tz_type_for_form.get(req_data.get("zn_tz_type"))(data=req_data)
        order_of_rel_form = OrderOfRelationForm(req_data)
        if form.is_valid() and order_of_rel_form.is_valid():
            order_of_relation = order_of_rel_form.cleaned_data["order_of_relation"]
            knowledge = form.save(commit=False)
            create_zn_for_constructor(knowledge, form, request)
            row_id = get_object_or_404(Tr, name="Строка").id
            column_id = get_object_or_404(Tr, name="Столбец").id
            if req_data.get("type_of_tr") == "row":
                create_relation(
                    table_id, knowledge.id, row_id, request.user, order_of_relation
                )
            else:
                create_relation(
                    table_id, knowledge.id, column_id, request.user, order_of_relation
                )
            return JsonResponse(
                {
                    "zn_id": knowledge.id,
                    "zn_name": knowledge.name,
                    "new_zn_tr_is_group": knowledge.tz.name == "Группа",
                },
                status=200,
            )
        return JsonResponse({}, status=400)


@require_http_methods(["GET", "POST"])
def element_of_group_in_table_create_update_view(request):
    if request.method == "GET":
        # Получение форм для создания знания
        if request.GET.get("action") == "create":
            zn_form = NameOfZnCreateUpdateForm()
            order_of_rel_form = OrderOfRelationForm()
        # Получение форм для редактирования знания
        else:
            current_zn = get_object_or_404(Znanie, id=request.GET.get("zn_id"))
            zn_form = NameOfZnCreateUpdateForm(instance=current_zn)
            order_of_relation = (
                Relation.objects.filter(rz_id=current_zn.id).first().order
            )
            order_of_rel_form = OrderOfRelationForm(
                initial={"order_of_relation": order_of_relation}
            )
        return JsonResponse(
            {
                "zn_form": f"{zn_form.as_p()}",
                "order_of_rel_form": f"{order_of_rel_form.as_p()}",
            }
        )
    else:
        # Сохранение нового/изменённого знания
        req_data = request.POST
        if req_data.get("action") == "edit":
            form = NameOfZnCreateUpdateForm(
                data=req_data,
                instance=get_object_or_404(Znanie, id=req_data.get("edited_zn_id")),
            )
        else:
            form = NameOfZnCreateUpdateForm(data=req_data)
        order_of_rel_form = OrderOfRelationForm(req_data)
        if form.is_valid() and order_of_rel_form.is_valid():
            order_of_relation = order_of_rel_form.cleaned_data["order_of_relation"]
            tz_id = get_object_or_404(Tz, name="Заголовок").id
            structure_kind = get_object_or_404(Tr, name="Состав").id
            knowledge = form.save(commit=False)
            create_zn_for_constructor(knowledge, form, request, tz_id=tz_id)
            parent_id = req_data.get("parent_for_element_of_group")
            create_relation(
                parent_id, knowledge.id, structure_kind, request.user, order_of_relation
            )
            return JsonResponse(
                {"zn_id": knowledge.id, "zn_name": knowledge.name}, status=200
            )
        return JsonResponse({}, status=400)


@require_http_methods(["GET"])
def get_cell_for_table(request):
    """Возвращает знание в ячейке, привязанное к строке, столбцу и таблице"""
    table_id = request.GET.get("table_id")
    row_id = request.GET.get("row_id")
    column_id = request.GET.get("column_id")
    zn_with_row = set(
        Relation.objects.filter(
            Q(rz_id=row_id) & Q(tr__name="Строка") & ~Q(bz_id=table_id)
        ).values_list("bz_id", flat=True)
    )
    zn_with_column = set(
        Relation.objects.filter(
            Q(rz_id=column_id) & Q(tr__name="Столбец") & ~Q(bz_id=table_id)
        ).values_list("bz_id", flat=True)
    )
    # Нахождение знания, привязанного и к строке, и к столбцу
    common_bz = zn_with_row & zn_with_column
    if common_bz:
        common_bz = common_bz.pop()
        # Проверка, привязано ли знание к таблице
        zn_with_table = Relation.objects.filter(
            Q(tr__name="Значение") & Q(bz_id=table_id) & Q(rz_id=common_bz)
        ).first()
        if zn_with_table:
            zn_in_cell = {common_bz: zn_with_table.rz.name}
            return JsonResponse(zn_in_cell, status=200)

    # Знания нет в ячейке
    return JsonResponse({}, status=200)


@require_http_methods(["POST"])
def create_zn_for_cell(request):
    """Создание нового знания для ячейки таблицы (с прикрепленными изображениями и файлом)"""
    req_data = request.POST
    form = ZnanieForCellCreateForm(data=req_data, user=request.user)
    images_form = ZnImageFormSet(req_data, get_images_from_request(request=request))
    file_form = ZnFilesFormSet(req_data, get_file_from_request(request=request))
    if form.is_valid() and images_form.is_valid() and file_form.is_valid():
        knowledge = form.save(commit=False)
        create_zn_for_constructor(
            knowledge, form, request, image_form=images_form, file_form=file_form
        )
        save_zn_to_cell_in_table(
            request.user,
            selected_table_id=request.POST.get("table_id"),
            selected_row_id=request.POST.get("row_id"),
            selected_column_id=request.POST.get("column_id"),
            selected_zn_for_cell_id=knowledge.id,
        )
        return JsonResponse(
            data={"zn_name": knowledge.name, "zn_id": knowledge.id}, status=200
        )
    return JsonResponse(data={}, status=400)


def save_zn_to_cell_in_table(
    user,
    selected_table_id,
    selected_row_id,
    selected_column_id,
    selected_zn_for_cell_id,
):
    """Удаляются раннее созданные связи с ячейкой, и создаются 3 связи с новым знанием"""
    row_id = get_object_or_404(Tr, name="Строка").id
    column_id = get_object_or_404(Tr, name="Столбец").id
    value_id = get_object_or_404(Tr, name="Значение").id
    row_relations = Relation.objects.filter(rz_id=selected_row_id)
    column_relations = Relation.objects.filter(rz_id=selected_column_id)
    cell_related_knowledges_id = []
    # Удаление связей "Строка" и "Столбец" с данной ячейкой
    for row_relation in row_relations:
        for column_relation in column_relations:
            if (row_relation.bz_id == column_relation.bz_id) and (
                str(row_relation.bz_id) != selected_table_id
            ):
                row_relation.delete()
                column_relation.delete()
                cell_related_knowledges_id.append(row_relation.bz_id)

    # Создание связи "Строка": базовое знание - выбранное знание, связанное знание - строка
    create_relation(selected_zn_for_cell_id, selected_row_id, row_id, user)

    # Создание связи "Столбец": базовое знание - выбранное знание, связанное знание - столбец
    create_relation(selected_zn_for_cell_id, selected_column_id, column_id, user)

    # Удаление предыдущей связи "Значение" с данной ячейкой
    for knowledge_id in cell_related_knowledges_id:
        Relation.objects.filter(bz_id=selected_table_id, rz_id=knowledge_id).delete()

    # Создание связи "Значение" : базовое знание - таблица, связанное знание - выбранное знание
    create_relation(selected_table_id, selected_zn_for_cell_id, value_id, user)


@require_http_methods(["POST"])
def save_zn_to_cell_in_table_from_request(request):
    new_relation_attrs = json.loads(request.body)
    save_zn_to_cell_in_table(
        request.user,
        selected_table_id=new_relation_attrs["table_id"],
        selected_row_id=new_relation_attrs["row_id"],
        selected_column_id=new_relation_attrs["column_id"],
        selected_zn_for_cell_id=new_relation_attrs["selected_zn_for_cell_id"],
    )

    return HttpResponse(status=200)


@require_http_methods(["DELETE"])
def delete_zn_in_cell_in_table(request):
    """Удаляются связи с выбранной ячейкой"""
    relation_attrs = json.loads(request.body)
    table_id = relation_attrs["table_id"]
    row_id = relation_attrs["row_id"]
    column_id = relation_attrs["column_id"]
    zn_in_cell_id = relation_attrs["selected_zn_for_cell_id"]
    rel_with_table = get_object_or_404(
        Relation, bz_id=table_id, rz_id=zn_in_cell_id, tr__name="Значение"
    )
    rel_with_row = get_object_or_404(
        Relation, bz_id=zn_in_cell_id, rz_id=row_id, tr__name="Строка"
    )
    rel_with_column = get_object_or_404(
        Relation, bz_id=zn_in_cell_id, rz_id=column_id, tr__name="Столбец"
    )

    # Если данный пользователь не является создателем связей с ячейкой, то запрещается удаление
    user_name_and_last_name = f"{request.user.first_name} {request.user.last_name}"
    if (
        rel_with_table.author.name != user_name_and_last_name
        or rel_with_row.author.name != user_name_and_last_name
        or rel_with_column.author.name != user_name_and_last_name
    ):
        return HttpResponse(status=422)

    rel_with_table.delete()
    rel_with_row.delete()
    rel_with_column.delete()

    return HttpResponse(status=200)


@require_http_methods(["DELETE"])
def delete_table(request):
    """
    Удаление таблицы. В таком случае удаляется все связи со связанными строками, столбцами и ячейками,
    затем сами строки, столбцы и ячейки (знания), затем таблица.
    """
    table_id = request.GET.get("id")
    group_in_table = request.GET.get("group_in_table")
    table = get_object_or_404(Znanie, id=table_id)
    tr_value_id = get_object_or_404(Tr, name="Значение").id
    # Если к таблице привязаны ячейки, запрещается удаление
    if Relation.objects.filter(bz_id=table_id, tr_id=tr_value_id).exists():
        return HttpResponse(status=422)
    # Удаление связей в случае, если в таблице есть строка/столбец вида "Группа"
    if group_in_table == "true":
        tr_row_id = get_object_or_404(Tr, name="Строка").id
        tr_column_id = get_object_or_404(Tr, name="Столбец").id
        # Нахождение связей "Строка", "Столбец", "Значение" с таблицей
        row_column_value_relations = Relation.objects.filter(bz_id=table_id)
        for row_column_value_relation in row_column_value_relations:
            if (
                row_column_value_relation.tr_id == tr_row_id
                or row_column_value_relation.tr_id == tr_column_id
            ):
                # Нахождение связей "Состав"
                structure_relations = Relation.objects.filter(
                    bz_id=row_column_value_relation.rz_id
                )
                if structure_relations:
                    for relation in structure_relations:
                        # Удаление связей "Строка" и "Столбец" с ячейками
                        Relation.objects.filter(rz_id=relation.rz_id).exclude(
                            bz_id=relation.bz_id
                        ).delete()
                        relation.bz.delete()
                        relation.rz.delete()
                else:
                    Relation.objects.filter(rz_id=relation.rz_id).delete()
                    if relation.rz.tz_id != tr_value_id:
                        relation.rz.delete()
        row_column_value_relations.delete()

    else:
        relations = Relation.objects.filter(bz_id=table_id)
        # Удаление связей, где базовым знанием является таблица
        for relation in relations:
            Relation.objects.filter(rz_id=relation.rz_id).delete()
            if relation.rz.tz_id != tr_value_id:
                relation.rz.delete()
    table.delete()

    return HttpResponse(status=200)


@require_http_methods(["DELETE"])
def delete_row_or_column(request):
    """Удаление строки/столбца. В таком случае удаляется связь с таблицей и сама строка/столбец"""
    znanie_id = request.GET.get("id")
    table_id = request.GET.get("table_id")
    is_group = request.GET.get("is_group")

    tr_row_id = get_object_or_404(Tr, name="Строка").id
    tr_column_id = get_object_or_404(Tr, name="Столбец").id
    structure_id = get_object_or_404(Tr, name="Состав").id

    # Если это группа и в ней есть элементы, запрещается удаление
    if is_group:
        if Relation.objects.filter(bz_id=znanie_id, tr_id=structure_id).exists():
            return HttpResponse(status=422)
    # Если есть ячейки, привязанные к строке/столбцу, запрещается удаление
    elif Relation.objects.filter(
        Q(rz_id=znanie_id)
        & ~Q(bz_id=table_id)
        & (Q(tr_id=tr_row_id) | Q(tr_id=tr_column_id))
    ):
        return HttpResponse(status=422)

    Relation.objects.filter(rz_id=znanie_id).delete()
    Znanie.objects.get(id=znanie_id).delete()
    return HttpResponse(status=200)


@require_http_methods(["DELETE"])
def delete_element_of_relation(request):
    """Удаление элемента строки/столбца. В таком случае удаляются связи со строкой/столбцом и сам элемент"""
    element_id = request.GET.get("id")
    relations = Relation.objects.filter(rz_id=element_id)

    tr_row_id = get_object_or_404(Tr, name="Строка").id
    tr_column_id = get_object_or_404(Tr, name="Столбец").id

    # Если есть ячейки, привязанные к элементу строки/столбца, запрещается удаление
    if Relation.objects.filter(
        Q(rz_id=element_id) & (Q(tr_id=tr_row_id) | Q(tr_id=tr_column_id))
    ):
        return HttpResponse(status=422)

    for relation in relations:
        relation.delete()

    Znanie.objects.get(id=element_id).delete()
    return HttpResponse(status=200)


@require_http_methods(["GET"])
def row_and_column_existence(request):
    """Проверка, есть ли в таблице хотя бы одна строка или столбец"""
    table_id = request.GET.get("id")

    is_row_and_column_exist = (
        Relation.objects.filter(
            tr__name="Строка", bz_id=table_id, is_published=True
        ).exists()
        and Relation.objects.filter(
            tr__name="Столбец", bz_id=table_id, is_published=True
        ).exists()
    )

    return JsonResponse({"is_row_and_column_exist": is_row_and_column_exist})


"""
 #####################################################################
 
 View конструктора таблиц и наполнения таблиц
 
 #####################################################################
"""


class PrevNextMixin:
    """
    Миксин для добавления referer в контекст
    Нужен чтобы кнопка Назад работала правильно
    Так же добавляется поддержка параметра next - перенаправление на другую страницу после успешного сохранения
    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # берем поле prev из POST, если его там нет - из HTTP_REFERER
        # по этому полю будем уходить по кнопке «Назад»
        if self.request.GET.get("next"):
            context["next"] = self.request.GET.get("next")

        if self.request.GET.get("prev"):
            context["prev"] = self.request.GET.get("prev")

        elif self.request.POST.get("prev"):
            context["prev"] = self.request.POST.get("prev")

        elif self.request.META.get("HTTP_REFERER"):
            context["prev"] = self.request.META.get("HTTP_REFERER")
        else:
            # если же пришли из ниоткуда - при закрытии уходим на главную страницу
            context["prev"] = "/"
        return context

    def form_valid(self):
        # если есть параметр next - уходим по нему
        # если нет - уходим по prev (только если там не корень)
        # если и его нет - уходим обратно на эту же страницу

        if self.request.POST.get("next"):
            return redirect(self.request.POST.get("next"))

        context = self.get_context_data()

        if "prev" in context:
            if context["prev"] != "/":
                return redirect(context["prev"])

        # если не было prev и next - остаемся на этой странице
        return self.get(self.request)


class TableConstructView(
    LoginRequiredMixin, DispatchMixin, PrevNextMixin, TemplateView
):
    """Представление для страницы «Конструктор таблицы»"""

    template_name = "drevo/constructors/table_construct.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        table = TableProxy(Znanie.objects.get(id=self.kwargs["pk"]))
        context["title"] = "Конструктор таблицы"
        context["table"] = table.knowledge
        context["table_info"] = json.dumps(table.get_header(), ensure_ascii=False)

        return context

    def post(self, request, *args, **kwargs):
        table_data = self.request.POST.get("table_info")
        if not table_data:
            raise ValueError("Не удалось получить данные таблицы")

        table_data = json.loads(table_data)

        knowledge = Znanie.objects.get(id=kwargs["pk"])
        table = TableProxy(knowledge)

        try:
            table.update_header(table_data)

        except KnowledgeProxyError as e:
            messages.warning(self.request, e)
            return self.form_invalid()

        return self.form_valid()

    def form_invalid(self):
        return self.get(self.request)


class TableFillingView(LoginRequiredMixin, DispatchMixin, PrevNextMixin, TemplateView):
    """Представление для страницы «Наполнение таблицы»"""

    template_name = "drevo/constructors/table_filling.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Наполнение таблицы"

        self.object = Znanie.objects.get(id=self.kwargs["pk"])
        context["object"] = self.object

        table = TableProxy(self.object)
        if table.is_zero_table():
            messages.warning(
                self.request, "Таблица пустая. Необходимо задать структуру"
            )

        if self.request.method == 'POST':
            context["table_data"] = self.request.POST.get("table_data")
            context["table_hash"] = self.request.POST.get("table_hash")
        else:
            header, cells = table.get_header_and_cells()
            context["table_data"] = json.dumps(cells, ensure_ascii=False)

            # Заголовки таблицы. Вдруг ее поменяют пока мы редактируем?
            # можно было бы посчитать хэш, но json тоже сойдет - размер таблиц не ожидается очень большой
            context["table_hash"] = json.dumps(header, ensure_ascii=False)

        # Это ужасное решение - гнать весь список в страницу. Тут нужен запрос на сервер!!!!
        context["knowledges"] = (
            Znanie.objects.filter(tz__is_systemic=False, is_published=True)
            .values("id", "name")
            .order_by("name")
        )
        return context

    def form_invalid(self):
        return self.get(self.request)

    def post(self, request, *args, **kwargs):
        def repeats(data: list[dict]):
            # возвращает объекты которые повторяются
            counter = Counter([(int(item["id"]), item["name"]) for item in data])
            result = [item[1] for item in counter if counter[item] > 1]
            return result

        self.object = Znanie.objects.get(id=kwargs["pk"])

        tbl = TableProxy(self.object)
        table_hash = json.loads(self.request.POST.get("table_hash"))
        table_data = json.loads(self.request.POST.get("table_data"))
        repeat = repeats(table_data)
        if repeat:
            messages.warning(request, f" Знания в таблице повторяются: {repeat}")
            return self.form_invalid()

        try:
            tbl.update_values(table_hash, table_data, self.request.user)

        except KnowledgeProxyError as e:
            messages.warning(request, str(e))
            return self.form_invalid()

        return self.form_valid()
