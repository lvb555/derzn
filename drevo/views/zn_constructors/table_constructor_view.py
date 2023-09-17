import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.generic import CreateView, UpdateView, FormView

from drevo.forms.knowledge_create_form import ZnImageFormSet
from drevo.forms.constructor_knowledge_form import (RelationCreateEditForm, NameOfZnCreateUpdateForm, AttributesOfZnForm,
                                                    ZnanieForCellCreateForm)
from drevo.models import BrowsingHistory, Znanie, Tz, Tr, Relation, SpecialPermissions, ZnImage

from .mixins import DispatchMixin
from .supplementary_functions import create_zn_for_constructor, create_relation
from drevo.views.my_interview_view import search_node_categories


def get_form_for_relation(type_of_relation, table_id):
    result = {
        'with_tz': True,
        'zn_create_form': RelationCreateEditForm,
        'zn_attr_form': AttributesOfZnForm
    }

    if type_of_relation == 'row':
        result['title'] = 'Создание строки'
        zn_filter = Q(tr__name='Строка', rz__tz__name='Заголовок')
    else:
        result['title'] = 'Создание столбца'
        zn_filter = Q(tr__name='Столбец', rz__tz__name='Заголовок')

    if Relation.objects.filter(bz_id=table_id).filter(zn_filter).exists():
        result['zn_create_form'] = NameOfZnCreateUpdateForm
        result['with_tz'] = False

    return result


class RelationCreateView(LoginRequiredMixin, FormView, DispatchMixin):
    """Представление создания знаний - строк и столбцов для таблицы"""
    model = Znanie
    template_name = 'drevo/table_constructor/table_relation_create.html'

    def __init__(self):
        super().__init__()
        self.relation = None
        self.table_id = None
        self.with_tz = True
        self.zn_create_form = None
        self.zn_attr_form = None

    def get_form_class(self):
        attr_for_context = get_form_for_relation(self.relation, self.table_id)
        self.zn_create_form = attr_for_context['zn_create_form']
        self.zn_attr_form = attr_for_context['zn_attr_form']
        return self.zn_create_form

    def get(self, *args, **kwargs):
        """Обрабатывает GET запрос"""
        self.object = None
        self.relation = self.kwargs.get('relation')
        self.table_id = self.kwargs.get('table_id')
        form_class = self.get_form_class()
        zn_create_form = self.get_form(form_class)
        zn_attr_form = AttributesOfZnForm()
        return self.render_to_response(self.get_context_data(zn_create_form=zn_create_form, zn_attr_form=zn_attr_form))

    def get_context_data(self, **kwargs):
        """Передает контекст в шаблон"""
        context = super().get_context_data(**kwargs)
        if self.relation == 'row':
            context['title'] = 'Создание строки'
        else:
            context['title'] = 'Создание столбца'

        # Передаем формы для создания знания
        if self.request.POST:
            context['zn_create_form'] = self.zn_create_form(self.request.POST)
            context['zn_attr_form'] = self.zn_attr_form(self.request.POST)
        else:
            context['zn_create_form'] = self.zn_create_form()
            context['zn_attr_form'] = self.zn_attr_form()
        return context

    def post(self, request, *args, **kwargs):
        """Обрабатывает POST запрос"""
        # self.object = None
        # Получаем форму для заполнения данных Знания
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        self.table_id = self.kwargs.get('table_id')
        self.relation = self.kwargs.get('relation')
        zn_attr_form = AttributesOfZnForm(self.request.POST)
        if form.is_valid() and zn_attr_form.is_valid():
            order_of_relation = zn_attr_form.cleaned_data['order_of_relation']
            knowledge = form.save(commit=False)
            create_zn_for_constructor(knowledge, form, request)
            row_id = get_object_or_404(Tr, name='Строка').id
            column_id = get_object_or_404(Tr, name='Столбец').id
            if self.relation == 'row':
                create_relation(self.table_id, knowledge.id, row_id, request, order_of_relation)
            else:
                create_relation(self.table_id, knowledge.id, column_id, request, order_of_relation)
            return render(request, 'drevo/table_constructor/table_relation_create.html', {
                'new': True,
                'new_znanie_name': knowledge.name,
                'new_znanie_id': knowledge.id,
                'new_znanie_kind': knowledge.tz.name,
            })

        return self.form_invalid(form, zn_attr_form)

    def form_invalid(self, form, zn_attr_form):
        return self.render_to_response(self.get_context_data(form=form, zn_attr_form=zn_attr_form))


class RelationEditView(LoginRequiredMixin, UpdateView, DispatchMixin):
    """Представление страницы изменения знаний - связей таблицы"""
    model = Znanie
    template_name = 'drevo/table_constructor/table_relation_edit.html'

    def __init__(self):
        super().__init__()
        self.relation = None
        self.parent_id = None

    def get_form_class(self):
        self.relation = self.kwargs.get('relation')
        if self.relation == 'element_row' or self.relation == 'element_column':
            return NameOfZnCreateUpdateForm
        else:
            return RelationCreateEditForm

    def get(self, *args, **kwargs):
        """Обрабатывает GET запрос"""
        self.relation = self.kwargs.get('relation')
        self.object = self.get_object()
        form_class = self.get_form_class()
        zn_edit_form = self.get_form(form_class)
        order_of_relation = Relation.objects.filter(rz_id=self.kwargs.get('pk')).first().order
        zn_attr_form = AttributesOfZnForm(initial={'order_of_relation': order_of_relation})
        return self.render_to_response(self.get_context_data(zn_edit_form=zn_edit_form, zn_attr_form=zn_attr_form))

    def get_context_data(self, **kwargs):
        """Передает контекст в шаблон"""
        context = super().get_context_data(**kwargs)
        relation_titles = {
            'row': 'строки',
            'column': 'столбца',
            'element_row': 'элемента группы строк',
            'element_column': 'элемента группы столбцов',
        }
        context['title'] = f'Редактирование {relation_titles.get(self.relation)}'
        context['pk'] = self.kwargs.get('pk')

        return context

    def post(self, request, *args, **kwargs):
        """Обрабатывает POST запрос"""
        self.object = self.get_object()
        self.relation = self.kwargs.get('relation')
        self.parent_id = self.kwargs.get('parent_id')
        # Получаем форму для заполнения данных Знания
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        zn_attr_form = AttributesOfZnForm(self.request.POST)
        if form.is_valid() and zn_attr_form.is_valid():
            row_id = get_object_or_404(Tr, name='Строка').id
            column_id = get_object_or_404(Tr, name='Столбец').id
            structure_id = get_object_or_404(Tr, name='Состав').id
            order_of_relation = zn_attr_form.cleaned_data['order_of_relation']
            knowledge = form.save(commit=False)
            create_zn_for_constructor(knowledge, form, request)
            if self.relation == 'row':
                create_relation(self.parent_id, knowledge.id, row_id, request, order_of_relation)
            elif self.relation == 'column':
                create_relation(self.parent_id, knowledge.id, column_id, request, order_of_relation)
            else:
                create_relation(self.parent_id, knowledge.id, structure_id, request, order_of_relation)
            return render(request, 'drevo/table_constructor/table_relation_edit.html', {
                'form': form,
                'changed_znanie_name': knowledge.name,
                'changed_znanie_id': knowledge.id,
                'relation': self.kwargs.get('relation'),
                'new': True
            })
        return self.form_invalid(form)


class GroupElementCreate(LoginRequiredMixin, CreateView, DispatchMixin):
    """Представление создания знаний - элементов строк и столбцов для таблицы"""
    model = Znanie
    form_class = NameOfZnCreateUpdateForm
    template_name = 'drevo/table_constructor/table_relation_create.html'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.table_id = None
        self.relation = None
        self.parent_id = None

    def get_context_data(self, **kwargs):
        """Передает контекст в шаблон"""
        context = super().get_context_data(**kwargs)
        self.relation = self.kwargs.get('relation')
        if self.relation == 'row':
            context['title'] = 'Ввод названия элемента группы строк'
        else:
            context['title'] = 'Ввод названия элемента группы столбцов'

        # Передаем формы для создания знания
        if self.request.POST:
            context['form'] = NameOfZnCreateUpdateForm(self.request.POST)
            context['zn_attr_form'] = AttributesOfZnForm(self.request.POST)
        else:
            context['form'] = NameOfZnCreateUpdateForm()
            context['zn_attr_form'] = AttributesOfZnForm()
        return context

    def get(self, *args, **kwargs):
        """Обрабатывает GET запрос"""
        self.object = None
        form_class = self.get_form_class()
        zn_create_form = self.get_form(form_class)
        zn_attr_form = AttributesOfZnForm()
        return self.render_to_response(self.get_context_data(zn_create_form=zn_create_form, zn_attr_form=zn_attr_form))

    def post(self, request, *args, **kwargs):
        """Обрабатывает POST запрос"""
        self.object = None
        # Получаем форму для заполнения данных Знания
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        zn_attr_form = AttributesOfZnForm(self.request.POST)
        if form.is_valid() and zn_attr_form.is_valid():
            order_of_relation = zn_attr_form.cleaned_data['order_of_relation']
            group_kind = get_object_or_404(Tz, name='Группа').id
            tz_id = get_object_or_404(Tz, name='Заголовок').id
            structure_kind = get_object_or_404(Tr, name='Состав').id
            knowledge = form.save(commit=False)
            create_zn_for_constructor(knowledge, form, request, tz_id=tz_id)
            self.parent_id = self.kwargs.get('parent_id')
            self.table_id = self.kwargs.get('table_id')
            create_relation(self.parent_id, knowledge.id, structure_kind, request, order_of_relation)

            return render(request, 'drevo/table_constructor/table_relation_create.html', {
                'form': form,
                'new': True,
                'new_znanie_name': knowledge.name,
                'new_znanie_id': knowledge.id,
                'row_is_group': Relation.objects.filter(bz_id=self.table_id, rz__tz_id=group_kind,
                                                        tr__name="Строка").exists(),
                'column_is_group': Relation.objects.filter(bz_id=self.table_id, rz__tz_id=group_kind,
                                                           tr__name="Столбец").exists()
            })
        return self.form_invalid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


class ZnForCellCreateView(LoginRequiredMixin, CreateView, DispatchMixin):
    """Представление создания знания - ячейки таблицы"""
    model = Znanie
    form_class = ZnanieForCellCreateForm
    template_name = 'drevo/filling_tables/create_zn_for_cell.html'

    def __init__(self):
        super().__init__()
        self.selected_table_id = None
        self.selected_row_id = None
        self.selected_column_id = None

    def get_context_data(self, **kwargs):
        """Передает контекст в шаблон"""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Создание знания'

        # Передаем формы для создания знания
        if self.request.POST:
            context['form'] = ZnanieForCellCreateForm(self.request.POST)
            context['image_form'] = ZnImageFormSet(self.request.POST)
        else:
            context['form'] = ZnanieForCellCreateForm(user=self.request.user)
            context['image_form'] = ZnImageFormSet()

        # Список всех опубликованных несистемных знаний в случае открытия страницы
        non_systemic_zn = Znanie.objects.filter(tz__is_systemic=False, is_published=True)
        zn_attributes = non_systemic_zn.values('id', 'name').order_by('name')
        context["non_systemic_zn"] = zn_attributes

        return context

    def get(self, request, *args, **kwargs):
        """Обрабатывает GET запрос"""
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        image_form = ZnImageFormSet()
        return self.render_to_response(self.get_context_data(form=form, image_form=image_form))

    def post(self, request, *args, **kwargs):
        """Обрабатывает POST запрос"""
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        # Получаем форму для заполнения данных Знания
        image_form = ZnImageFormSet(self.request.POST, self.request.FILES)
        if form.is_valid() and image_form.is_valid():
            tz_id = Tz.objects.get(name='Заголовок').id
            knowledge = form.save(commit=False)
            create_zn_for_constructor(knowledge, form, request, tz_id=tz_id, author=True, image_form=image_form)

            non_systemic_zn = Znanie.objects.filter(tz__is_systemic=False, is_published=True)
            zn_attributes = non_systemic_zn.values('id', 'name').order_by('name')
            return render(request, 'drevo/filling_tables/create_zn_for_cell.html', {
                'form': form,
                'new': True,
                'new_znanie_name': knowledge.name,
                'new_znanie_id': knowledge.id,
                'non_systemic_zn': zn_attributes
            })
        return self.form_invalid(form)

    def form_invalid(self, form, image_form):
        return self.render_to_response(self.get_context_data(form=form, image_form=image_form))


def filling_tables(request, pk):
    """
    Отображение страницы "Ввод табличных значений"
    """
    expert = get_object_or_404(SpecialPermissions, expert=request.user)

    if expert:
        context = get_contex_data(pk)
        template_name = "drevo/filling_tables/filling_tables.html"
        return render(request, template_name, context)

    return HttpResponseRedirect(reverse('drevo'))


def get_cell_for_table(request):
    """Возвращает знание в ячейке, привязанное к строке и столбцу таблицы"""
    data = json.loads(request.body)
    table_id = data['id_table']
    row_id = data['id_row']
    column_id = data['id_column']

    zn_with_row = Relation.objects.filter(Q(rz_id=row_id) & Q(tr__name='Строка') & ~Q(bz_id=table_id)).first().bz
    zn_with_column = Relation.objects.filter(
        Q(rz_id=column_id) & Q(tr__name='Столбец') & ~Q(bz_id=table_id)).first().bz
    zn_with_table = Relation.objects.filter(Q(tr__name='Значение') & Q(bz_id=table_id)).first().rz

    if zn_with_row and zn_with_column and zn_with_table and zn_with_row == zn_with_column == zn_with_table:

        zn_in_cell = {zn_with_row.id: zn_with_row.name}
        return JsonResponse(zn_in_cell)


def save_zn_to_cell_in_table(request):
    """Удаляются раннее созданные знания в ячейке, и создаются 3 связи с новым знанием"""
    row_id = get_object_or_404(Tr, name='Строка').id
    column_id = get_object_or_404(Tr, name='Столбец').id
    value_id = get_object_or_404(Tr, name='Значение').id

    data = json.loads(request.body)
    selected_table_id = data['table_id']
    selected_row_id = data['row_id']
    selected_column_id = data['column_id']
    selected_zn_for_cell_id = data['znanie_in_cell_id']

    # Если знание еще не в ячейке, то выполняются следующие действия
    if not (Relation.objects.filter(rz_id=selected_row_id, bz_id=selected_zn_for_cell_id).exists() and
            Relation.objects.filter(rz_id=selected_column_id, bz_id=selected_zn_for_cell_id).exists() and
            Relation.objects.filter(rz_id=selected_zn_for_cell_id, bz_id=selected_table_id).exists()):

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


def table_constructor(request, pk):
    """
    Отображение страницы "Конструктор таблиц"
    """
    expert = get_object_or_404(SpecialPermissions, expert=request.user)

    if expert:
        context = get_contex_data(pk, table_create=True)
        template_name = "drevo/table_constructor/table_constructor.html"
        return render(request, template_name, context)

    return HttpResponseRedirect(reverse('drevo'))


def get_contex_data(pk, table_create=False):
    """
    Получение выбранной таблицы, связанных с ней строк и столбцов, а также несистемных знаний
    в случае работы со страницей "Наполнение таблиц"
    """
    context = {}

    if table_create:
        context["title"] = 'Конструктор таблиц'
    else:
        context["title"] = 'Наполнение таблиц'

    if pk == '0':
        context["new_table"] = True
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

    if table_create:
        group_kind = get_object_or_404(Tz, name='Группа').id
        structure_kind = get_object_or_404(Tr, name='Состав').id
        relation_row_group = Relation.objects.filter(bz_id=table_id, rz__tz_id=group_kind, tr__name="Строка").first()
        if relation_row_group:
            row_group_structure = Relation.objects.filter(bz_id=relation_row_group.rz_id, tr_id=structure_kind)
            rows_structure_attributes = row_group_structure.values('rz_id', 'rz__name').order_by('-rz__order')
            context["rows_structure_attributes"] = rows_structure_attributes
            context["row_is_group"] = True

        relation_column_group = Relation.objects.filter(bz_id=table_id, rz__tz_id=group_kind,
                                                        tr__name="Столбец").first()
        if relation_column_group:
            column_group_structure = Relation.objects.filter(bz_id=relation_column_group.rz_id, tr_id=structure_kind)
            columns_structure_attributes = column_group_structure.values('rz_id', 'rz__name').order_by('-rz__order')
            context["columns_structure_attributes"] = columns_structure_attributes
            context["column_is_group"] = True

    context["table_dict"] = table_attributes
    context["rows_attributes"] = rows_attributes
    context["columns_attributes"] = columns_attributes

    return context


def show_filling_tables_page(request):
    """
    Возвращает True для показа страницы «Наполнение таблиц», если существует хотя бы одна таблица в компетенции
    эксперта и в ней есть хотя бы одна строка и столбец
    """

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

        data = False
        for table, table_id in enumerate(table_dict):
            if Relation.objects.filter(tr__name='Строка', bz_id=table_id,
                                       is_published=True).exists() and Relation.objects.filter(
                                       tr__name='Столбец', bz_id=table_id, is_published=True).exists():
                data = True

    return JsonResponse([data], safe=False)


def delete_table(request):
    """
    Удаление таблицы. В таком случае удаляется все связи со связанными строками, столбцами и ячейками,
    затем сами строки, столбцы и ячейки (знания) затем таблица.
    """
    data = json.loads(request.body)
    table_id = data['id']
    group_in_table = data['group_in_table']
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

    dat = True
    return JsonResponse([dat], safe=False)


def delete_row_or_column(request):
    """Удаление строки/столбца. В таком случае удаляется связь, связанная со строкой/столбцом, затем
    удаляется сама строка/столбец и ячейка (знания)."""
    data = json.loads(request.body)
    znanie_id = data['id']
    is_group = data['is_group']
    dat = True

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
    return JsonResponse([dat], safe=False)


def delete_element_of_relation(request):
    """Удаление элемента строки/столбца. В таком случае удаляются связи со строкой, столбцом, таблицей,
    и сам элемент"""
    data = json.loads(request.body)
    element_id = data['id']
    relations = Relation.objects.filter(rz_id=element_id)
    dat = True

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

    return JsonResponse([dat], safe=False)


def row_and_column_existence(request):
    """Проверка, есть ли в таблице хотя бы одна строка или столбец"""
    data = json.loads(request.body)
    table_id = data['id']
    data = False
    row_id = get_object_or_404(Tr, name='Строка').id
    column_id = get_object_or_404(Tr, name='Столбец').id

    is_row_exist = Relation.objects.filter(tr_id=row_id, bz_id=table_id,
                                           is_published=True).exists()
    is_column_exist = Relation.objects.filter(tr_id=column_id, bz_id=table_id,
                                              is_published=True).exists()

    if not is_row_exist and not is_column_exist:
        return JsonResponse({'relations': 'not'})
    elif not is_row_exist and is_column_exist:
        return JsonResponse({'relations': 'column'})
    elif is_row_exist and not is_column_exist:
        return JsonResponse({'relations': 'row'})
    else:
        return JsonResponse({'relations': 'all'})


def cell_in_table_or_relation_existence(request):
    """1 вариант: Проверка, есть ли в таблице хотя бы одна ячейка
    2 вариант: Проверка, привязано ли знание к строке или столбцу"""
    value_id = get_object_or_404(Tr, name='Значение').id
    structure_kind = get_object_or_404(Tr, name='Состав').id
    data = json.loads(request.body)
    znanie_id = data['id']
    is_table = data['table']
    is_group = data['is_group']
    data = False
    # Если передана таблица, проверка на наличие ячейки
    if is_table:
        if Relation.objects.filter(tr_id=value_id, bz_id=znanie_id, is_published=True).exists():
            data = True
    # Если передана строка/столбец, проверка, привязано ли знание
    else:
        # Если знание - группа, то проверяем привязку к знанию в каждом элементе строки/столбца
        if is_group:
            relations = Relation.objects.filter(bz_id=znanie_id, tr_id=structure_kind)
            for relation in relations:
                if Relation.objects.filter(rz_id=relation.rz_id, is_published=True).exclude(bz_id=znanie_id).exists():
                    data = True
        # В противном случае проверяем, есть ли ячейка, привязанная к данному знанию
        else:
            if Relation.objects.filter(tr_id=value_id, rz_id=znanie_id, is_published=True).exists():
                data = True
    return JsonResponse(data, safe=False)
