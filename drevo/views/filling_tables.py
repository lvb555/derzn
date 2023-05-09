import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, TemplateView, UpdateView

from drevo.forms.knowledge_create_form import RelationCreateForm, TableCreateForm, ZnImageFormSet
from drevo.forms.knowledge_update_form import ZnImageEditFormSet, TableUpdateForm
from drevo.models import Author, BrowsingHistory, Category, KnowledgeStatuses, Znanie, Tz, Tr, Relation, \
    SpecialPermissions, ZnImage

from .my_interview_view import search_node_categories


def get_knowledge_dict(knowledge, rights, user=None):
    """
    Возвращает кортеж, который содержит кверисет с категориями и
    словарь, в котором ключи - категории, а значения - знания
    :param knowledge: кверисет со знаниями
    :param user: ползьзователь
    :param rights: права пользователя (эксперт/руководитель)
    :return: кортеж: (категории, {категория: знания})
    """
    _knowledge_dict = {}
    # формирует список категорий
    _categories = Category.tree_objects.exclude(is_published=False)

    for category in _categories:
        if user:
            if rights == 'expert':
                experts = category.get_expert_ancestors_category()
            else:
                experts = category.get_admin_ancestors_category()

            if user in experts:
                zn_in_this_category = knowledge.filter(
                    category=category)
                # Проверка, существуют ли в данной категории знания. Категория добавляется только в том
                # случае, если существует хотя бы одно знание
                if zn_in_this_category:
                    _knowledge_dict[category.name] = zn_in_this_category
        else:
            zn_in_this_category = knowledge.filter(
                category=category)
            if not zn_in_this_category:
                continue
            _knowledge_dict[category.name] = zn_in_this_category
    result_categories = []
    for category in _categories:
        if category.name in _knowledge_dict.keys():
            result_categories.append(category)
    return result_categories, _knowledge_dict


class TableKnowledgeTreeView(LoginRequiredMixin, TemplateView):
    """
    Представление страницы дерева табличных знаний
    """
    template_name = 'drevo/table_create_and_update.html'

    def dispatch(self, request, *args, **kwargs):
        expert = get_object_or_404(SpecialPermissions, expert=request.user)
        if not expert:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

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

        context['ztypes'], context['zn_dict'] = get_knowledge_dict(zn, rights='expert', user=user)
        context['title'] = 'Дерево табличных знаний'

        return context


class CreateChangeTableView(LoginRequiredMixin, TemplateView):
    """
    Представление страницы создания/изменения таблиц
    """
    template_name = 'drevo/table_create_and_update.html'

    def dispatch(self, request, *args, **kwargs):
        expert = get_object_or_404(SpecialPermissions, expert=request.user)
        if not expert:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Передает контекст в шаблон"""
        context = super().get_context_data(**kwargs)
        user = self.request.user
        # Формирование списка знаний вида "Таблица" со статусом "Опубликованное знание"
        zn = Znanie.objects.filter(
            Q(tz__name='Таблица') & Q(knowledge_status__status='PUB')
        )
        context['ztypes'], context['zn_dict'] = get_knowledge_dict(zn, rights='admin', user=user)
        context['title'] = 'Создание и изменение таблиц'
        context['table_create'] = True

        return context


class TableCreateView(LoginRequiredMixin, CreateView):
    """Представление создания знания вида Таблица"""
    model = Znanie
    form_class = TableCreateForm
    template_name = 'drevo/table_create.html'
    success_url = reverse_lazy("table_constructor")

    def dispatch(self, request, *args, **kwargs):
        """Проверка перед открытием страницы, является ли пользователь экспертом"""
        expert = get_object_or_404(SpecialPermissions, expert=request.user)
        if not expert:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        """Передает контекст в шаблон"""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Создание таблицы'

        # Передаем формы для создания знания и добавления фотографий к знанию
        if self.request.POST:
            context['form'] = TableCreateForm(self.request.POST)
            context['image_form'] = ZnImageFormSet(self.request.POST)
        else:
            context['form'] = TableCreateForm(user=self.request.user)
            context['image_form'] = ZnImageFormSet()
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
        # Получаем форму для заполнения данных Знания
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        # Получаем форму для прикрепления фотографий
        image_form = ZnImageFormSet(self.request.POST, self.request.FILES)
        if form.is_valid() and image_form.is_valid():
            # Перед сохранением формы в поле user подставляем значения по умолчанию
            knowledge = form.save(commit=False)
            knowledge.is_published = True
            knowledge.user = request.user
            # Сохраняем Знание
            knowledge.save()
            form.save_m2m()
            # Перед сохранением формы с изображениями подставляем текущий объект знания
            image_form.instance = knowledge
            image_form.save()
            # Создание записи
            KnowledgeStatuses.objects.create(
                knowledge=knowledge,
                status='PUB',
                user=self.request.user
            )
            return render(request, 'drevo/table_create.html', {
                'form': form,
                'new_znanie_name': knowledge.name,
                'new_znanie_id': knowledge.id,
                'new': True,
            })

        return self.form_invalid(form, image_form)

    def form_invalid(self, form, image_form):
        return self.render_to_response(self.get_context_data(form=form, image_form=image_form))


class TableEditView(LoginRequiredMixin, UpdateView):
    """Представление редактирования знания вида Таблица"""
    model = Znanie
    form_class = TableUpdateForm
    template_name = 'drevo/table_edit.html'
    success_url = reverse_lazy("table_constructor")

    def dispatch(self, request, *args, **kwargs):
        """Проверка перед открытием страницы, является ли пользователь экспертом"""
        expert = get_object_or_404(SpecialPermissions, expert=request.user)
        if not expert:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        """Передает контекст в шаблон"""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактирование таблицы'
        context['pk'] = self.kwargs.get('pk')
        return context

    def get(self, request, *args, **kwargs):
        """Обрабатывает GET запрос"""
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        image_form = ZnImageFormSet()
        return self.render_to_response(self.get_context_data(form=form, image_form=image_form))

    def post(self, request, *args, **kwargs):
        """Обрабатывает POST запрос"""
        self.object = self.get_object()
        # Получаем форму для заполнения данных Знания
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        # Получаем форму для прикрепления фотографий
        image_form = ZnImageEditFormSet(self.request.POST, self.request.FILES, instance=self.object)
        if form.is_valid() and image_form.is_valid():
            # Перед сохранением формы в поле user подставляем значения по умолчанию
            knowledge = form.save(commit=False)
            knowledge.user = request.user
            # Сохраняем Знание
            knowledge.save()
            form.save_m2m()
            # Перед сохранением формы с изображениями подставляем текущий объект знания
            image_form.instance = knowledge
            image_form.save()

            return render(request, 'drevo/table_edit.html', {
                'form': form,
                'changed_znanie_name': knowledge.name,
                'changed_znanie_id': knowledge.id,
                'new': True,
            })

        return self.form_invalid(form, image_form)

    def form_invalid(self, form, image_form):
        return self.render_to_response(self.get_context_data(form=form, image_form=image_form))


class RelationCreateView(LoginRequiredMixin, CreateView):
    """Представление создания знаний - строк и столбцов для таблицы"""
    model = Znanie
    form_class = RelationCreateForm
    template_name = 'drevo/relation_create.html'
    success_url = reverse_lazy("table_constructor")

    def dispatch(self, request, *args, **kwargs):
        """Проверка перед открытием страницы, является ли пользователь экспертом"""
        expert = get_object_or_404(SpecialPermissions, expert=request.user)
        if not expert:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Передает контекст в шаблон"""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Создание знания'

        # Передаем формы для создания знания
        if self.request.POST:
            context['form'] = RelationCreateForm(self.request.POST)
        else:
            context['form'] = RelationCreateForm()

        heading_knowledges = Znanie.objects.filter(tz__name='Заголовок')
        zn_attributes = heading_knowledges.values('id', 'name').order_by('name')
        context["heading_knowledges"] = zn_attributes
        return context

    def get(self, request, *args, **kwargs):
        """Обрабатывает GET запрос"""
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        return self.render_to_response(self.get_context_data(form=form))

    def post(self, request, *args, **kwargs):
        """Обрабатывает POST запрос"""
        self.object = None
        # Получаем форму для заполнения данных Знания
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            tz_id = Tz.objects.get(name='Заголовок').id
            # Перед сохранением формы в поле user подставляем текущего пользователя
            knowledge = form.save(commit=False)
            author, created = Author.objects.get_or_create(
                name=f"{request.user.first_name} {request.user.last_name}",
            )
            knowledge.author_id = author.id
            knowledge.tz_id = tz_id
            knowledge.is_published = True
            knowledge.user = request.user
            # Сохраняем Знание
            knowledge.save()
            form.save_m2m()
            # Создание записи
            KnowledgeStatuses.objects.create(
                knowledge=knowledge,
                status='PUB',
                user=self.request.user
            )
            heading_knowledges = Znanie.objects.filter(tz__name='Заголовок')
            zn_attributes = heading_knowledges.values('id', 'name').order_by('name')
            return render(request, 'drevo/relation_create.html', {
                'form': form,
                'new': True,
                'new_znanie_name': knowledge.name,
                'new_znanie_id': knowledge.id,
                'heading_knowledges': zn_attributes
            })
        return self.form_invalid(form)

    def form_invalid(self, form, image_form):
        return self.render_to_response(self.get_context_data(form=form, image_form=image_form))


class RelationEditView(LoginRequiredMixin, UpdateView):
    """Представление страницы изменения знаний - связей таблицы"""
    model = Znanie
    form_class = RelationCreateForm
    template_name = 'drevo/relation_edit.html'
    success_url = reverse_lazy("table_constructor")

    def dispatch(self, request, *args, **kwargs):
        """Проверка перед открытием страницы, является ли пользователь экспертом"""
        expert = get_object_or_404(SpecialPermissions, expert=request.user)
        if not expert:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Передает контекст в шаблон"""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактирование знания'
        context['pk'] = self.kwargs.get('pk')
        return context

    def get(self, request, *args, **kwargs):
        """Обрабатывает GET запрос"""
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        return self.render_to_response(self.get_context_data(form=form))

    def post(self, request, *args, **kwargs):
        """Обрабатывает POST запрос"""
        self.object = self.get_object()
        # Получаем форму для заполнения данных Знания
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            # Перед сохранением формы в поле user подставляем текущего пользователя
            knowledge = form.save(commit=False)
            author, created = Author.objects.get_or_create(
                name=f"{request.user.first_name} {request.user.last_name}",
            )
            knowledge.author_id = author.id
            knowledge.user = request.user
            # Сохраняем Знание
            knowledge.save()
            form.save_m2m()
            return render(request, 'drevo/relation_edit.html', {
                'form': form,
                'changed_znanie_name': knowledge.name,
                'changed_znanie_id': knowledge.id,
                'relation': self.kwargs.get('relation'),
                'pk': knowledge.id,
                'new': True
            })
        return self.form_invalid(form)


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

    if not table_create:
        # Список всех опубликованных несистемных знаний в случае открытия страницы "Наполнение таблиц"
        non_systemic_zn = Znanie.objects.filter(tz__is_systemic=False)
        zn_attributes = non_systemic_zn.values('id', 'name').order_by('name')
        context["non_systemic_zn"] = zn_attributes

    context["table_dict"] = table_attributes
    context["rows_attributes"] = rows_attributes
    context["columns_attributes"] = columns_attributes

    return context


def show_filling_tables_page(request):
    """
    Возвращает True для показа страницы «Наполнение таблиц», если существует хотя бы одна таблица в компетенции
    эксперта и в ней есть хотя бы одна строка и столбец
    """

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
    # Проверка, открыта ли страница "Наполнение таблиц"
    filling_tables_page = request.POST.get('filling_tables')
    # Нахождение id связей с именами "Строка" и "Столбец"
    row_id = get_object_or_404(Tr, name='Строка').id
    column_id = get_object_or_404(Tr, name='Столбец').id
    if filling_tables_page:
        value_id = get_object_or_404(Tr, name='Значение').id
    # Получение значений выбранной таблицы, знания, строки и столбца
    selected_table_pk = request.POST.get('table')
    selected_row_pk = request.POST.get('row')
    selected_column_pk = request.POST.get('column')
    if filling_tables_page:
        selected_znanie_pk = request.POST.get('znanie')

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

    if filling_tables_page:

        # Удаление связей со знанием/знаниями, которые раньше находились в этой ячейке
        row_relations = Relation.objects.filter(rz_id=selected_row_pk)
        column_relations = Relation.objects.filter(rz_id=selected_column_pk)
        cell_related_knowledges_id = []
        # Удаление связей "Строка" и "Столбец" с данной ячейкой
        for row_relation in row_relations:
            for column_relation in column_relations:
                if (row_relation.bz_id == column_relation.bz_id) and (str(row_relation.bz_id) != selected_table_pk):
                    row_relation.delete()
                    column_relation.delete()
                    cell_related_knowledges_id.append(row_relation.bz_id)
        # Удаление связи "Значение" с данной ячейкой
        for knowledge_id in cell_related_knowledges_id:
            Relation.objects.filter(bz_id=selected_table_pk, rz_id=knowledge_id).delete()

        # Создание связи "Строка": связанное знание - строка, базовое знание - выбранное знание
        create_relation(row_id, selected_row_pk, selected_znanie_pk)

        # Создание связи "Столбец": связанное знание - столбец, базовое знание - выбранное знание
        create_relation(column_id, selected_column_pk, selected_znanie_pk)

        # Создание связи "Значение" : связанное знание - выбранное знание, базовое знание - таблица
        create_relation(value_id, selected_znanie_pk, selected_table_pk)

    else:
        # Создание связи "Строка": базовое знание - таблица, связанное знание - строка
        if selected_row_pk:
            create_relation(row_id, selected_row_pk, selected_table_pk)

        # Создание связи "Столбец": базовое знание - таблица, связанное знание - столбец
        if selected_column_pk:
            create_relation(column_id, selected_column_pk, selected_table_pk)

    return HttpResponse('Данные были успешно сохранены')


def delete_table(request):
    """
    Удаление таблицы. В таком случае удаляется все связи со связанными строками, столбцами и ячейками,
    затем сами строки, столбцы и ячейки (знания) затем таблица.
    """
    data = json.loads(request.body)
    table_id = data['id']
    table = Znanie.objects.get(id=table_id)
    relations = Relation.objects.filter(bz_id=table_id)
    related_knowledges = []

    # Удаление просмотра таблицы при его существовании (protect объект)
    BrowsingHistory.objects.filter(znanie=table).delete()

    # Удаление фотографий, связанных со знанием (protect-объект)
    ZnImage.objects.filter(znanie=table).delete()

    for relation in relations:
        related_knowledges.append(relation.rz)

    # Удаление связей, где базовым знанием является таблица
    Relation.objects.filter(bz_id=table_id).delete()
    for knowledge in related_knowledges:
        # Удаление связей, где базовым знанием является связанное с таблицей знание
        Relation.objects.filter(bz=knowledge).delete()
        # Удаление знаний, связанных с таблицей
        knowledge.delete()
    # Удаление таблицы
    table.delete()
    dat = True
    return JsonResponse([dat], safe=False)


def delete_row_or_column(request):
    """Удаление строки/столбца. В таком случае удаляется связь, связанная со строкой/столбцом, затем
    удаляется сама строка/столбец и ячейка (знания)."""
    data = json.loads(request.body)
    znanie_id = data['id']
    relations = Relation.objects.filter(rz_id=znanie_id)
    related_knowledges = []
    for relation in relations:
        related_knowledges.append(relation.bz)
    dat = True
    # Удаление связей, где связанным знанием является выбранное знание
    Relation.objects.filter(rz_id=znanie_id).delete()
    table_tz = Tz.objects.get(name="Таблица").id
    for knowledge in related_knowledges:
        # Удаление связей, связанных и базовых знаний в случае, если знание не таблица
        if knowledge.tz_id != table_tz:
            Relation.objects.filter(rz_id=knowledge.id).delete()
            Relation.objects.filter(bz_id=knowledge.id).delete()
            knowledge.delete()
    Znanie.objects.get(id=znanie_id).delete()
    return JsonResponse([dat], safe=False)


def row_and_column_existence(request):
    """Проверка, есть ли в таблице хотя бы одна строка или столбец"""
    data = json.loads(request.body)
    table_id = data['id']
    data = False
    row_id = get_object_or_404(Tr, name='Строка').id
    column_id = get_object_or_404(Tr, name='Столбец').id
    if Relation.objects.filter(tr_id=row_id, bz_id=table_id,
                               is_published=True).exists() and Relation.objects.filter(
        tr_id=column_id, bz_id=table_id, is_published=True).exists():
        data = True
    return JsonResponse(data, safe=False)
