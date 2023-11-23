import json

from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods
from django.views.generic import TemplateView

from drevo.forms.knowledge_create_form import ZnImageFormSet, ZnFilesFormSet
from drevo.forms.constructor_knowledge_form import (ZnanieForRowOrColumnForm, NameOfZnCreateUpdateForm,
                                                    OrderOfRelationForm,
                                                    ZnanieForCellCreateForm, MainZnInConstructorCreateEditForm)
from drevo.models import BrowsingHistory, Znanie, Tz, Tr, Relation, SpecialPermissions, ZnImage

from .mixins import DispatchMixin
from .supplementary_functions import create_relation, create_zn_for_constructor, get_images_from_request, \
    get_file_from_request
from drevo.views.my_interview_view import search_node_categories


def show_filling_tables_page(request):
    """
    Страница «Наполнение таблиц» доступна, если существует хотя бы одна таблица в компетенции
    эксперта и в ней есть хотя бы одна строка и столбец
    """
    result = {'show': False}
    expert = get_object_or_404(SpecialPermissions, expert=request.user)

    if expert:

        categories_expert = expert.categories.all()
        categories = search_node_categories(categories_expert)
        zn_queryset = Znanie.objects.filter(tz__name='Таблица', is_published=True)

        # Выбор опубликованных знаний вида "Таблица" в пределах компетенции эксперта
        table_dict = {}
        for category in categories:
            zn_in_this_category = zn_queryset.filter(category=category).order_by('name')

            for zn in zn_in_this_category:
                table_dict[zn.pk] = zn.name

        for table, table_id in enumerate(table_dict):
            if (Relation.objects
                    .filter(tr__name='Строка', bz_id=table_id, is_published=True)
                    .exists() and
                    Relation.objects
                            .filter(tr__name='Столбец', bz_id=table_id, is_published=True)
                            .exists()):
                result['show'] = True

    return JsonResponse(result, safe=False)


def get_contex_data(pk, user=None, table_create=False):
    """
    Получение данных для страниц "Наполнение таблиц", "Конструктор таблиц"
    """
    context = {}
    selected_table = get_object_or_404(Znanie, id=pk)
    table_id = pk

    # Получение id и имени знаний, связанных с таблицей с помощью вида "Строка"
    selected_rows = Relation.objects.filter(tr__name="Строка", bz_id=table_id)
    rows_attributes = selected_rows.values('rz_id', 'rz__name').order_by('-rz__order')

    # Получение id и имени знаний, связанных с таблицей с помощью вида "Столбец"
    selected_columns = Relation.objects.filter(tr__name="Столбец", bz_id=table_id)
    columns_attributes = selected_columns.values('rz_id', 'rz__name').order_by('-rz__order')

    if table_create:
        context["title"] = 'Конструктор таблиц'
        group_kind = get_object_or_404(Tz, name='Группа').id
        structure_kind = get_object_or_404(Tr, name='Состав').id
        relation_row_group = Relation.objects.filter(bz_id=table_id, rz__tz_id=group_kind, tr__name="Строка").first()
        if relation_row_group:
            # Получение id и имени знаний, связанных со строкой с помощью вида "Состав"
            row_group_structure = Relation.objects.filter(bz_id=relation_row_group.rz_id, tr_id=structure_kind)
            rows_structure_attributes = row_group_structure.values('rz_id', 'rz__name').order_by('-rz__order')
            context["rows_structure_attributes"] = rows_structure_attributes
            context["row_is_group"] = True

        relation_column_group = Relation.objects.filter(bz_id=table_id, rz__tz_id=group_kind,
                                                        tr__name="Столбец").first()
        if relation_column_group:
            # Получение id и имени знаний, связанных со столбцом с помощью вида "Состав"
            column_group_structure = Relation.objects.filter(bz_id=relation_column_group.rz_id, tr_id=structure_kind)
            columns_structure_attributes = column_group_structure.values('rz_id', 'rz__name').order_by('-rz__order')
            context["columns_structure_attributes"] = columns_structure_attributes
            context["column_is_group"] = True

        # Формы для редактирования главного знания - таблицы
        main_zn_edit_form = MainZnInConstructorCreateEditForm(instance=selected_table,
                                                              user=user,
                                                              type_of_zn='table')
        context['main_zn_edit_form'] = main_zn_edit_form
        context['main_zn_edit_form_uuid'] = main_zn_edit_form.fields['content'].widget.attrs['id']
        context['images_form_for_main_zn'] = ZnImageFormSet(instance=selected_table)
        context['file_form_for_main_zn'] = ZnFilesFormSet(instance=selected_table)
    else:
        context["title"] = f'Наполнение таблицы <{selected_table.name}>'
        # Формы для создания знания в ячейке таблицы
        form = ZnanieForCellCreateForm(user=user)
        context['form'] = form
        context['zn_form_uuid'] = form.fields['content'].widget.attrs['id']
        context['images_form'] = ZnImageFormSet()
        context['file_form'] = ZnFilesFormSet()

        # Список всех опубликованных несистемных знаний для ячейки таблицы
        non_systemic_zn = Znanie.objects.filter(tz__is_systemic=False, is_published=True)
        zn_attributes = non_systemic_zn.values('id', 'name').order_by('name')
        context["non_systemic_zn"] = zn_attributes

    context["main_zn_name"] = selected_table.name
    context["main_zn_id"] = selected_table.id
    context["rows_attributes"] = rows_attributes
    context["columns_attributes"] = columns_attributes

    return context


class TableConstructorView(DispatchMixin, TemplateView):
    """Представление для страницы «Конструктор таблиц»"""
    template_name = "drevo/constructors/table_constructor.html"

    def get_context_data(self, **kwargs):
        return get_contex_data(pk=self.kwargs.get('pk'), table_create=True, user=self.request.user)


class FillingTablesView(DispatchMixin, TemplateView):
    """Представление для страницы «Наполнение таблицы»"""
    template_name = "drevo/constructors/filling_tables.html"

    def get_context_data(self, **kwargs):
        return get_contex_data(pk=self.kwargs.get('pk'), user=self.request.user)


@require_http_methods(['GET', 'POST'])
def relation_in_table_create_update_view(request):
    tz_type_for_form = {
        'heading': NameOfZnCreateUpdateForm,
        'any_type': ZnanieForRowOrColumnForm
    }
    if request.method == 'GET':
        # Получение форм для создания знания
        if request.GET.get('action') == 'create':
            zn_form = tz_type_for_form.get(request.GET.get('zn_tz_type'))()
            order_of_rel_form = OrderOfRelationForm()
        # Получение форм для редактирования знания
        else:
            current_zn = get_object_or_404(Znanie, id=request.GET.get('zn_id'))
            zn_form = ZnanieForRowOrColumnForm(instance=current_zn)
            order_of_relation = Relation.objects.filter(rz_id=current_zn.id).first().order
            order_of_rel_form = OrderOfRelationForm(initial={'order_of_relation': order_of_relation})
        return JsonResponse({'zn_form': f'{zn_form.as_p()}', 'order_of_rel_form': f'{order_of_rel_form.as_p()}'})
    else:
        # Сохранение нового/изменённого знания
        req_data = request.POST
        table_id = req_data.get('table_id')
        if req_data.get('action') == 'edit':
            form = tz_type_for_form.get(req_data.get('zn_tz_type'))(data=req_data,
                                                                    instance=get_object_or_404
                                                                    (Znanie, id=req_data.get('edited_zn_id')))
        else:
            form = tz_type_for_form.get(req_data.get('zn_tz_type'))(data=req_data)
        order_of_rel_form = OrderOfRelationForm(req_data)
        if form.is_valid() and order_of_rel_form.is_valid():
            order_of_relation = order_of_rel_form.cleaned_data['order_of_relation']
            knowledge = form.save(commit=False)
            create_zn_for_constructor(knowledge, form, request)
            row_id = get_object_or_404(Tr, name='Строка').id
            column_id = get_object_or_404(Tr, name='Столбец').id
            if req_data.get('type_of_tr') == 'row':
                create_relation(table_id, knowledge.id, row_id, request, order_of_relation)
            else:
                create_relation(table_id, knowledge.id, column_id, request, order_of_relation)
            return JsonResponse({'zn_id': knowledge.id, 'zn_name': knowledge.name,
                                 'new_zn_tr_is_group': knowledge.tz.name == 'Группа'}, status=200)
        return JsonResponse({}, status=400)


@require_http_methods(['GET', 'POST'])
def element_of_group_in_table_create_update_view(request):
    if request.method == 'GET':
        # Получение форм для создания знания
        if request.GET.get('action') == 'create':
            zn_form = NameOfZnCreateUpdateForm()
            order_of_rel_form = OrderOfRelationForm()
        # Получение форм для редактирования знания
        else:
            current_zn = get_object_or_404(Znanie, id=request.GET.get('zn_id'))
            zn_form = NameOfZnCreateUpdateForm(instance=current_zn)
            order_of_relation = Relation.objects.filter(rz_id=current_zn.id).first().order
            order_of_rel_form = OrderOfRelationForm(initial={'order_of_relation': order_of_relation})
        return JsonResponse({'zn_form': f'{zn_form.as_p()}', 'order_of_rel_form': f'{order_of_rel_form.as_p()}'})
    else:
        # Сохранение нового/изменённого знания
        req_data = request.POST
        if req_data.get('action') == 'edit':
            form = NameOfZnCreateUpdateForm(data=req_data,
                                            instance=get_object_or_404
                                            (Znanie, id=req_data.get('edited_zn_id')))
        else:
            form = NameOfZnCreateUpdateForm(data=req_data)
        order_of_rel_form = OrderOfRelationForm(req_data)
        if form.is_valid() and order_of_rel_form.is_valid():
            order_of_relation = order_of_rel_form.cleaned_data['order_of_relation']
            tz_id = get_object_or_404(Tz, name='Заголовок').id
            structure_kind = get_object_or_404(Tr, name='Состав').id
            knowledge = form.save(commit=False)
            create_zn_for_constructor(knowledge, form, request, tz_id=tz_id)
            parent_id = req_data.get('parent_for_element_of_group')
            create_relation(parent_id, knowledge.id, structure_kind, request, order_of_relation)
            return JsonResponse({'zn_id': knowledge.id, 'zn_name': knowledge.name}, status=200)
        return JsonResponse({}, status=400)


@require_http_methods(['GET'])
def get_cell_for_table(request):
    """Возвращает знание в ячейке, привязанное к строке и столбцу таблицы"""
    table_id = request.GET.get('table_id')
    row_id = request.GET.get('row_id')
    column_id = request.GET.get('column_id')

    zn_with_row = Relation.objects.filter(Q(rz_id=row_id) & Q(tr__name='Строка') & ~Q(bz_id=table_id)).first()
    zn_with_column = Relation.objects.filter(
        Q(rz_id=column_id) & Q(tr__name='Столбец') & ~Q(bz_id=table_id)).first()
    zn_with_table = Relation.objects.filter(Q(tr__name='Значение') & Q(bz_id=table_id)).first()
    if zn_with_row and zn_with_column and zn_with_table and zn_with_row.bz == zn_with_column.bz == zn_with_table.rz:
        zn_in_cell = {zn_with_row.bz_id: zn_with_row.bz.name}
        return JsonResponse(zn_in_cell, status=200)

    # Знания нет в ячейке
    return JsonResponse({}, status=200)


@require_http_methods(['POST'])
def create_zn_for_cell(request):
    """Создание нового знания для ячейки таблицы(с прикрепленными изображениями и файлом)"""
    req_data = request.POST
    form = ZnanieForCellCreateForm(data=req_data, user=request.user)
    images_form = ZnImageFormSet(req_data, get_images_from_request(request=request))
    file_form = ZnFilesFormSet(req_data, get_file_from_request(request=request))
    if form.is_valid() and images_form.is_valid() and file_form.is_valid():
        knowledge = form.save(commit=False)
        create_zn_for_constructor(knowledge, form, request, image_form=images_form, file_form=file_form)
        return JsonResponse(data={'zn_name': knowledge.name, 'zn_id': knowledge.id}, status=200)
    return JsonResponse(data={}, status=400)


@require_http_methods(['POST'])
def save_zn_to_cell_in_table(request):
    """Удаляются раннее созданные знания в ячейке, и создаются 3 связи с новым знанием"""
    row_id = get_object_or_404(Tr, name='Строка').id
    column_id = get_object_or_404(Tr, name='Столбец').id
    value_id = get_object_or_404(Tr, name='Значение').id

    new_relation_attrs = json.loads(request.body)
    selected_table_id = new_relation_attrs['table_id']
    selected_row_id = new_relation_attrs['row_id']
    selected_column_id = new_relation_attrs['column_id']
    selected_zn_for_cell_id = new_relation_attrs['selected_zn_for_cell_id']

    # Удаление связей со знанием/знаниями, которые раньше находились в этой ячейке
    row_relations = Relation.objects.filter(rz_id=selected_row_id)
    column_relations = Relation.objects.filter(rz_id=selected_column_id)
    cell_related_knowledges_id = []
    # Удаление связей "Строка" и "Столбец" с данной ячейкой
    for row_relation in row_relations:
        for column_relation in column_relations:
            if (row_relation.bz_id == column_relation.bz_id) and (str(row_relation.bz_id) != selected_table_id):
                row_relation.delete()
                column_relation.delete()
                cell_related_knowledges_id.append(row_relation.bz_id)

    # Создание связи "Строка": базовое знание - выбранное знание, связанное знание - строка
    create_relation(selected_zn_for_cell_id, selected_row_id, row_id, request)

    # Создание связи "Столбец": базовое знание - выбранное знание, связанное знание - столбец
    create_relation(selected_zn_for_cell_id, selected_column_id, column_id, request)

    # Удаление предыдущей связи "Значение" с данной ячейкой
    for knowledge_id in cell_related_knowledges_id:
        Relation.objects.filter(bz_id=selected_table_id, rz_id=knowledge_id).delete()

    # Создание связи "Значение" : базовое знание - таблица, связанное знание - выбранное знание
    create_relation(selected_table_id, selected_zn_for_cell_id, value_id, request)

    return HttpResponse(status=200)


@require_http_methods(['GET'])
def delete_table(request):
    """
    Удаление таблицы. В таком случае удаляется все связи со связанными строками, столбцами и ячейками,
    затем сами строки, столбцы и ячейки (знания), затем таблица.
    """
    table_id = request.GET.get('id')
    group_in_table = request.GET.get('group_in_table')
    table = Znanie.objects.get(id=table_id)

    # Удаление просмотра таблицы при его существовании (protect-объект)
    BrowsingHistory.objects.filter(znanie=table).delete()

    # Удаление фотографий, связанных со знанием (protect-объект)
    ZnImage.objects.filter(znanie=table).delete()

    # Удаление связей в случае, если в таблице есть строка/столбец вида "Группа"
    if group_in_table:
        tr_row_id = get_object_or_404(Tr, name='Строка').id
        tr_column_id = get_object_or_404(Tr, name='Столбец').id
        # Нахождение связей "Строка", "Столбец", "Значений" с таблицей
        row_column_value_relations = Relation.objects.filter(bz_id=table_id)
        for row_column_value_relation in row_column_value_relations:
            if row_column_value_relation.tr_id == tr_row_id or row_column_value_relation.tr_id == tr_column_id:
                # Нахождение связей "Состав"
                structure_relations = Relation.objects.filter(bz_id=row_column_value_relation.rz_id)
                if structure_relations:
                    for relation in structure_relations:
                        # Удаление связей "Строка" и "Столбец" с ячейками
                        Relation.objects.filter(rz_id=relation.rz_id).exclude(bz_id=relation.bz_id).delete()
                    structure_relations.delete()
                else:
                    Relation.objects.filter(rz_id=row_column_value_relation.rz_id).delete()
        row_column_value_relations.delete()

    else:
        relations = Relation.objects.filter(bz_id=table_id)
        # Удаление связей, где базовым знанием является таблица
        relations.delete()
        for relation in relations:
            # Удаление связей, где базовым знанием является связанное с таблицей знание
            Relation.objects.filter(bz_id=relation.rz_id).delete()

    table.delete()

    return HttpResponse(status=200)


@require_http_methods(['GET'])
def delete_row_or_column(request):
    """Удаление строки/столбца. В таком случае удаляется связь, связанная со строкой/столбцом, затем
    удаляется сама строка/столбец и ячейка (знания)."""
    znanie_id = request.GET.get('id')
    is_group = request.GET.get('is_group')

    table_tz_id = get_object_or_404(Tz, name="Таблица").id
    tr_row_id = get_object_or_404(Tr, name='Строка').id
    tr_column_id = get_object_or_404(Tr, name='Столбец').id

    if is_group:
        Relation.objects.filter(rz_id=znanie_id).delete()
        relations_with_elements = Relation.objects.filter(bz_id=znanie_id)
        for relation_with_element in relations_with_elements:
            relations_with_cell = Relation.objects.filter(rz_id=relation_with_element.rz_id)
            # Удаление связей с элементами строки/столбца
            relation_with_element.delete()
            for relation in relations_with_cell:
                if relation.tr_id == tr_row_id or relation.tr_id == tr_column_id:
                    cell_related_knowledge = relation.bz
                    # Удаление связи "Строка"/"Столбец", связывающую элемент строки/столбца и знание в ячейке
                    relation.delete()
                    Relation.objects.filter(bz=cell_related_knowledge).delete()
                    # Удаление знания в ячейке
                    cell_related_knowledge.delete()

    else:
        relations_with_table = Relation.objects.filter(rz_id=znanie_id)
        related_knowledges = []
        for relation in relations_with_table:
            related_knowledges.append(relation.bz)

        # Удаление связей, где связанным знанием является выбранное знание
        Relation.objects.filter(rz_id=znanie_id).delete()
        for knowledge in related_knowledges:
            # Удаление связей, связанных и базовых знаний в случае, если знание не таблица
            if knowledge.tz_id != table_tz_id:
                Relation.objects.filter(rz_id=knowledge.id).delete()
                Relation.objects.filter(bz_id=knowledge.id).delete()
                # Удаление знания в ячейке
                knowledge.delete()
    Znanie.objects.get(id=znanie_id).delete()
    return HttpResponse(status=200)


@require_http_methods(['GET'])
def delete_element_of_relation(request):
    """Удаление элемента строки/столбца. В таком случае удаляются связи со строкой, столбцом, таблицей,
    и сам элемент"""
    element_id = request.GET.get('id')
    relations = Relation.objects.filter(rz_id=element_id)

    tr_row_id = get_object_or_404(Tr, name='Строка').id
    tr_column_id = get_object_or_404(Tr, name='Столбец').id

    for relation in relations:
        if relation.tr_id == tr_row_id or relation.tr_id == tr_column_id:
            cell_related_knowledge = relation.bz
            relation.delete()
            cell_related_knowledge.delete()
            Relation.objects.filter(bz=cell_related_knowledge).delete()
        else:
            relation.delete()

    Znanie.objects.get(id=element_id).delete()
    return HttpResponse(status=200)


@require_http_methods(['GET'])
def row_and_column_existence(request):
    """Проверка, есть ли в таблице хотя бы одна строка или столбец"""
    table_id = request.GET.get('id')

    is_row_and_column_exist = (
            Relation.objects.filter(tr__name='Строка', bz_id=table_id, is_published=True).exists() and
            Relation.objects.filter(tr__name='Столбец', bz_id=table_id, is_published=True).exists()
    )

    return JsonResponse({'is_row_and_column_exist': is_row_and_column_exist})
