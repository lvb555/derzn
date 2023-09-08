from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.generic import CreateView, TemplateView, UpdateView

from drevo.forms.knowledge_create_form import ZnImageFormSet
from drevo.forms.constructor_knowledge_form import MainZnInConstructorCreateEditForm
from drevo.forms.knowledge_update_form import ZnImageEditFormSet
from drevo.models import Znanie, Tr, Relation

from drevo.views.knowledge_tp_view import get_knowledge_dict
from .supplementary_functions import create_zn_for_constructor
from drevo.relations_tree import get_descendants_for_knowledge
from .mixins import FormKwargsMixin, DispatchMixin


class ConstructorTreeView(LoginRequiredMixin, DispatchMixin, TemplateView):
    """
    Представление страницы дерева знаний конструкторов в компетенциях эксперта/руководителя
    """
    template_name = 'drevo/constructor_tree.html'

    def __init__(self, **kwargs):
        super().__init__()
        self.type_of_zn = None

    def get_context_data(self, **kwargs):
        """Передает контекст в шаблон"""
        context = super().get_context_data(**kwargs)
        user = self.request.user
        self.type_of_zn = self.kwargs.get('type_of_zn')
        tz_name_mapping = {
            'algorithm': 'Алгоритм',
            'filling_tables': 'Таблица',
            'table': 'Таблица',
            'test': 'Тест',
        }

        # Формирование списка знаний со статусом "Опубликованное знание" в соответствии с выбранным конструктором
        zn = Znanie.objects.filter(
            Q(tz__name=tz_name_mapping.get(self.type_of_zn)) & Q(knowledge_status__status='PUB')
        )

        if self.type_of_zn == 'filling_tables':
            for znanie in zn:
                row_id = get_object_or_404(Tr, name='Строка').id
                column_id = get_object_or_404(Tr, name='Столбец').id
                # Проверка, существуют ли в таблице опубликованные строка и столбец
                if not (Relation.objects.filter(tr_id=row_id, bz_id=znanie.id, is_published=True).exists() and
                        Relation.objects.filter(tr_id=column_id, bz_id=znanie.id, is_published=True).exists()):
                    zn = zn.exclude(id=znanie.id)

        if self.type_of_zn == 'table':
            context['ztypes'], context['zn_dict'] = get_knowledge_dict(zn, rights='admin', user=user)
        else:
            context['ztypes'], context['zn_dict'] = get_knowledge_dict(zn, rights='expert', user=user)

        title_mapping = {
            'filling_tables': 'Наполнение таблиц',
            'table': 'Конструктор таблиц',
            'test': 'Конструктор тестов',
            'algorithm': 'Конструктор алгоритмов',
        }
        context['title'] = title_mapping.get(self.type_of_zn)
        context['type_of_page'] = self.type_of_zn

        return context


class MainZnInConstructorCreateView(FormKwargsMixin, DispatchMixin, LoginRequiredMixin, CreateView):
    """Представление создания главного для конструктора знания (виды Тест, Таблица, Алгоритм)"""
    model = Znanie
    form_class = MainZnInConstructorCreateEditForm

    def get_template_names(self):
        self.type_of_zn = self.kwargs.get('type_of_zn')
        if self.type_of_zn == 'table':
            return ['drevo/table_constructor/table_relation_create.html']
        elif self.type_of_zn == 'test':
            return ['drevo/quiz_constructor/quiz_question_answer_create.html']
        elif self.type_of_zn == 'algorithm':
            return ['drevo/algorithm_constructor/algorithm_create.html']

    def get_context_data(self, **kwargs):
        """Передает контекст в шаблон"""
        context = super().get_context_data(**kwargs)
        title_mapping = {
            'algorithm': 'Создание названия алгоритма',
            'table': 'Создание названия таблицы',
            'test': 'Создание названия теста',
        }
        self.type_of_zn = self.kwargs.get('type_of_zn')
        context['title'] = title_mapping.get(self.type_of_zn)

        # Передаем формы для создания знания и добавления фотографий к знанию
        if self.request.POST:
            context['zn_create_form'] = MainZnInConstructorCreateEditForm(self.request.POST, type_of_zn=self.type_of_zn)
            context['image_form'] = ZnImageFormSet(self.request.POST)
        else:
            context['zn_create_form'] = MainZnInConstructorCreateEditForm(user=self.request.user, type_of_zn=self.type_of_zn)
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
        self.type_of_zn = self.kwargs.get('type_of_zn')
        # Получаем форму для заполнения данных Знания
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        # Получаем форму для прикрепления фотографий
        image_form = ZnImageFormSet(self.request.POST, self.request.FILES)
        if form.is_valid() and image_form.is_valid():
            # Перед сохранением формы в поле user подставляем значения по умолчанию
            knowledge = form.save(commit=False)
            create_zn_for_constructor(knowledge, form, request, author=False, image_form=image_form)
            self.object = knowledge
            if self.type_of_zn == 'algorithm':
                context = {
                    'title': 'Конструктор алгоритмов',
                    'znanie': knowledge,
                    'relative_znaniya': get_descendants_for_knowledge(knowledge)
                }
            else:
                context = {
                    'form': form,
                    'new_znanie_name': knowledge.name,
                    'new_znanie_id': knowledge.id,
                    'new': True,
                    'type_of_zn': self.type_of_zn
                }
            if self.type_of_zn == 'table':
                return render(request, 'drevo/table_constructor/table_relation_create.html', context)
            elif self.type_of_zn == 'test':
                return render(request, 'drevo/quiz_constructor/quiz_question_answer_create.html', context)
            elif self.type_of_zn == 'algorithm':
                return HttpResponseRedirect(reverse('algorithm_constructor', kwargs={'pk': knowledge.pk}))

        return self.form_invalid(form, image_form)

    def form_invalid(self, form, image_form):
        return self.render_to_response(self.get_context_data(form=form, image_form=image_form))


class MainZnInConstructorEditView(FormKwargsMixin, DispatchMixin, LoginRequiredMixin, UpdateView):
    """Представление редактирования главного для конструктора знания (виды Тест, Таблица, Алгоритм)"""
    model = Znanie
    form_class = MainZnInConstructorCreateEditForm
    template_name = 'drevo/quiz_constructor/quiz_question_answer_edit.html'

    def get_context_data(self, **kwargs):
        """Передает контекст в шаблон"""
        context = super().get_context_data(**kwargs)
        title_mapping = {
            'table': 'Редактирование названия таблицы',
            'test': 'Редактирование названия теста',
            'algorithm': 'Редактирование названия алгоритма',
        }
        self.type_of_zn = self.kwargs.get('type_of_zn')
        context['title'] = title_mapping.get(self.type_of_zn)
        context['pk'] = self.kwargs.get('pk')
        return context

    def get(self, request, *args, **kwargs):
        """Обрабатывает GET запрос"""
        self.object = self.get_object()
        form_class = self.get_form_class()
        zn_edit_form = self.get_form(form_class)
        image_form = ZnImageFormSet()
        return self.render_to_response(self.get_context_data(zn_edit_form=zn_edit_form, image_form=image_form))

    def post(self, request, *args, **kwargs):
        """Обрабатывает POST запрос"""
        self.object = self.get_object()
        self.type_of_zn = self.kwargs.get('type_of_zn')
        # Получаем форму для заполнения данных Знания
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        # Получаем форму для прикрепления фотографий
        image_form = ZnImageEditFormSet(self.request.POST, self.request.FILES, instance=self.object)
        if form.is_valid() and image_form.is_valid():
            # Перед сохранением формы в поле user подставляем значения по умолчанию
            knowledge = form.save(commit=False)
            create_zn_for_constructor(knowledge, form, request, author=False, image_form=image_form)

            context = {
                'form': form,
                'changed_znanie_name': knowledge.name,
                'changed_znanie_id': knowledge.id,
                'new': True,
                'relation': self.type_of_zn,
            }
            if self.type_of_zn == 'table':
                return render(request, 'drevo/table_constructor/table_relation_edit.html', context)
            elif self.type_of_zn == 'test':
                return render(request, 'drevo/quiz_constructor/quiz_question_answer_edit.html', context)
            else:
                pass

        return self.form_invalid(form)

    def form_invalid(self, form):
        image_form = ZnImageEditFormSet(self.request.POST, self.request.FILES, instance=self.object)
        return self.render_to_response(self.get_context_data(form=form, image_form=image_form))
