import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, TemplateView, UpdateView

from drevo.forms.knowledge_create_form import RelationCreateForm, TableOrQuizCreateEditForm, ZnImageFormSet, NameOfZnanieCreateUpdateForm
from drevo.forms.knowledge_update_form import ZnImageEditFormSet
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
    template_name = 'drevo/table_quiz_constructor_tree.html'

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
            if not (Relation.objects.filter(tr_id=row_id, bz_id=z.id, is_published=True).exists() and
                    Relation.objects.filter(tr_id=column_id, bz_id=z.id, is_published=True).exists()):
                zn = zn.exclude(id=z.id)

        context['ztypes'], context['zn_dict'] = get_knowledge_dict(zn, rights='expert', user=user)
        context['title'] = 'Наполнение таблиц'
        context['type_of_page'] = 'filling_tables'

        return context


class CreateChangeTableView(LoginRequiredMixin, TemplateView):
    """
    Представление страницы создания/изменения таблиц
    """
    template_name = 'drevo/table_quiz_constructor_tree.html'

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
        context['title'] = 'Конструктор таблиц'
        context['type_of_page'] = 'table_constructor'

        return context


class TableCreateView(LoginRequiredMixin, CreateView):
    """Представление создания знания вида Таблица"""
    model = Znanie
    form_class = TableOrQuizCreateEditForm
    template_name = 'drevo/filling_tables/table_create.html'
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
        kwargs['type_of_zn'] = 'Таблица'
        return kwargs

    def get_context_data(self, **kwargs):
        """Передает контекст в шаблон"""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Создание таблицы'

        # Передаем формы для создания знания и добавления фотографий к знанию
        if self.request.POST:
            context['form'] = TableOrQuizCreateEditForm(self.request.POST)
            context['image_form'] = ZnImageFormSet(self.request.POST)
        else:
            context['form'] = TableOrQuizCreateEditForm(user=self.request.user, type_of_zn='Таблица')
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
            return render(request, 'drevo/filling_tables/table_create.html', {
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
    form_class = TableOrQuizCreateEditForm
    template_name = 'drevo/filling_tables/table_edit.html'
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
        kwargs['type_of_zn'] = 'Таблица'
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

            return render(request, 'drevo/filling_tables/table_edit.html', {
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
    template_name = 'drevo/filling_tables/relation_create.html'
    success_url = reverse_lazy("table_constructor")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.with_tz = True

    def get_form_class(self, *args, **kwargs):
        table_id = self.kwargs.get('table_id')
        if self.kwargs.get('relation') == 'row':
            if Relation.objects.filter(bz_id=table_id, tr__name='Строка', rz__tz__name='Заголовок').exists():
                self.with_tz = False
                return NameOfZnanieCreateUpdateForm
            return RelationCreateForm
        else:
            if Relation.objects.filter(bz_id=table_id, tr__name='Столбец', rz__tz__name='Заголовок').exists():
                self.with_tz = False
                return NameOfZnanieCreateUpdateForm
            return RelationCreateForm

    def dispatch(self, request, *args, **kwargs):
        """Проверка перед открытием страницы, является ли пользователь экспертом"""
        expert = get_object_or_404(SpecialPermissions, expert=request.user)
        if not expert:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Передает контекст в шаблон"""
        context = super().get_context_data(**kwargs)
        if self.kwargs.get('relation') == 'row':
            context['title'] = 'Создание строки'
        else:
            context['title'] = 'Создание столбца'

        # Передаем формы для создания знания
        if self.request.POST:
            if self.with_tz:
                context['form'] = RelationCreateForm(self.request.POST)
            else:
                context['form'] = NameOfZnanieCreateUpdateForm(self.request.POST)
        else:
            if self.with_tz:
                context['form'] = RelationCreateForm()
            else:
                context['form'] = NameOfZnanieCreateUpdateForm()

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
            # Перед сохранением формы в поле user подставляем текущего пользователя
            knowledge = form.save(commit=False)
            if form_class.__name__ == 'NameOfZnanieCreateUpdateForm':
                tz_id = get_object_or_404(Tz, name='Заголовок').id
                knowledge.tz_id = tz_id
            author, created = Author.objects.get_or_create(
                name=f"{request.user.first_name} {request.user.last_name}",
            )
            knowledge.author_id = author.id
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
            return render(request, 'drevo/filling_tables/relation_create.html', {
                'form': form,
                'new': True,
                'new_znanie_name': knowledge.name,
                'new_znanie_id': knowledge.id,
                'new_znanie_kind': knowledge.tz.name,
            })
        return self.form_invalid(form)

    def form_invalid(self, form, image_form):
        return self.render_to_response(self.get_context_data(form=form, image_form=image_form))


class RelationEditView(LoginRequiredMixin, UpdateView):
    """Представление страницы изменения знаний - связей таблицы"""
    model = Znanie
    form_class = NameOfZnanieCreateUpdateForm
    template_name = 'drevo/filling_tables/relation_edit.html'
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
            return render(request, 'drevo/filling_tables/relation_edit.html', {
                'form': form,
                'changed_znanie_name': knowledge.name,
                'changed_znanie_id': knowledge.id,
                'relation': self.kwargs.get('relation'),
                'new': True
            })
        return self.form_invalid(form)


class GroupElementCreate(LoginRequiredMixin, CreateView):
    """Представление создания знаний - строк и столбцов для таблицы"""
    model = Znanie
    form_class = NameOfZnanieCreateUpdateForm
    template_name = 'drevo/filling_tables/relation_create.html'
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
            context['form'] = NameOfZnanieCreateUpdateForm(self.request.POST)
        else:
            context['form'] = NameOfZnanieCreateUpdateForm()

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
            tz_id = get_object_or_404(Tz, name='Заголовок').id
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
            return render(request, 'drevo/filling_tables/relation_create.html', {
                'form': form,
                'new': True,
                'new_znanie_name': knowledge.name,
                'new_znanie_id': knowledge.id,
            })
        return self.form_invalid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


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


def table_constructor(request, pk):
    """
    Отображение страницы "Конструктор таблиц"
    """
    expert = get_object_or_404(SpecialPermissions, expert=request.user)

    if expert:
        context = get_contex_data(pk, table_create=True)
        template_name = "drevo/filling_tables/table_constructor.html"
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

    else:
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


def create_relation(bz_id, rz_id, tr_id, request):
    """Создание опубликованной связи с заданными параметрами"""

    # Создание автора с именем и фамилией пользователя, если такого не существует
    author, created = Author.objects.get_or_create(
        name=f"{request.user.first_name} {request.user.last_name}",
    )

    # Создание опубликованной связи с выбранными значениями, если оно не было создано
    Relation.objects.get_or_create(
        bz_id=bz_id,
        tr_id=tr_id,
        rz_id=rz_id,
        author_id=author.id,
        is_published=True,
        defaults={'user_id': request.user.id}
    )


def get_form_data(request):
    """
    Создание трех связей таблицы, строки, столбца и значения при условии, что заполнены все поля
    """
    # Проверка, открыта ли страница "Наполнение таблиц"
    filling_tables_page = request.POST.get('filling_tables')
    # Нахождение id связей с именами "Строка" и "Столбец"
    row_id = get_object_or_404(Tr, name='Строка').id
    column_id = get_object_or_404(Tr, name='Столбец').id
    structure_id = get_object_or_404(Tr, name='Состав').id
    if filling_tables_page:
        value_id = get_object_or_404(Tr, name='Значение').id
    else:
        group_kind = get_object_or_404(Tz, name='Группа').id
        # Получение значений выбранных элементов в группах "Строка" и "Столбец"
        selected_row_element_pk = request.POST.get('row_element')
        selected_column_element_pk = request.POST.get('column_element')
    # Получение значений выбранной таблицы, знания, строки и столбца
    selected_table_pk = request.POST.get('table')
    selected_row_pk = request.POST.get('row')
    selected_column_pk = request.POST.get('column')
    if filling_tables_page:
        selected_znanie_pk = request.POST.get('znanie')

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

        # Создание связи "Строка": базовое знание - выбранное знание, связанное знание - строка
        create_relation(selected_znanie_pk, selected_row_pk, row_id, request)

        # Создание связи "Столбец": базовое знание - выбранное знание, связанное знание - столбец
        create_relation(selected_znanie_pk, selected_column_pk, column_id, request)

        # Создание связи "Значение" : связанное знание - выбранное знание, базовое знание - таблица
        create_relation(selected_table_pk, selected_znanie_pk, value_id, request)

    else:
        # Создание связи "Строка": базовое знание - таблица, связанное знание - строка
        if selected_row_pk:
            create_relation(selected_table_pk, selected_row_pk, row_id, request)
        # Создание связи "Столбец": базовое знание - таблица, связанное знание - столбец
        if selected_column_pk:
            create_relation(selected_table_pk, selected_column_pk, column_id, request)
        # Создание связи "Состав": базовое знание - строка таблицы, связанное знание - элемент строки
        if selected_row_element_pk:
            create_relation(selected_row_pk, selected_row_element_pk, structure_id, request)
        # Создание связи "Состав": базовое знание - столбец таблицы, связанное знание - элемент столбца
        if selected_column_element_pk:
            create_relation(selected_column_pk, selected_column_element_pk, structure_id, request)

    response = {
        'row_is_group': Relation.objects.filter(bz_id=selected_table_pk, rz__tz_id=group_kind,
                                                tr__name="Строка").exists(),
        'column_is_group': Relation.objects.filter(bz_id=selected_table_pk, rz__tz_id=group_kind,
                                                   tr__name="Столбец").exists(),
    }
    return JsonResponse(response, safe=False)


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
    if Relation.objects.filter(tr_id=row_id, bz_id=table_id,
                               is_published=True).exists() and Relation.objects.filter(
        tr_id=column_id, bz_id=table_id, is_published=True).exists():
        data = True
    return JsonResponse(data, safe=False)


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
