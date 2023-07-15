import json
import re

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, TemplateView, UpdateView

from drevo.forms.knowledge_create_form import NameOfZnanieCreateUpdateForm, TableOrQuizCreateEditForm, ZnImageFormSet, \
    QuestionToQuizCreateForm, AnswerToQuizCreateForm
from drevo.forms.knowledge_update_form import ZnImageEditFormSet
from drevo.models import Author, BrowsingHistory, Category, KnowledgeStatuses, Znanie, Tz, Tr, Relation, \
    SpecialPermissions

from .table_constructor_view import create_relation, get_knowledge_dict


class QuizConstructorTreeView(LoginRequiredMixin, TemplateView):
    """
    Представление страницы дерева знаний вида "Тест" в компетенциях эксперта
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
        # Формирование списка знаний вида "Тест" со статусом "Опубликованное знание"
        zn = Znanie.objects.filter(
            Q(tz__name='Тест') & Q(knowledge_status__status='PUB')
        )

        context['ztypes'], context['zn_dict'] = get_knowledge_dict(zn, rights='expert', user=user)
        context['title'] = 'Конструктор тестов'
        context['type_of_page'] = 'quiz_constructor'

        return context


class QuizConstructorView(LoginRequiredMixin, TemplateView):
    """
    Отображение страницы "Конструктор тестов"
    """
    template_name = 'drevo/quiz_constructor/quiz_constructor.html'

    def dispatch(self, request, *args, **kwargs):
        expert = get_object_or_404(SpecialPermissions, expert=request.user)
        if not expert:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Передает контекст в шаблон"""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Конструктор тестов'
        pk = self.kwargs.get('pk')
        if pk == '0':
            context["new_test"] = True
            return context

        selected_quiz = Znanie.objects.get(id=pk)
        test_attributes = {selected_quiz.id: selected_quiz.name}
        context["test_attributes"] = test_attributes

        selected_questions = Relation.objects.filter(bz_id=pk, tr__name="Состав")
        questions_attributes = selected_questions.values('rz_id', 'rz__name').order_by('rz__name')
        if questions_attributes:
            context["questions_attributes"] = questions_attributes

        return context


class QuizCreateView(LoginRequiredMixin, CreateView):
    """Представление создания знания вида Тест"""
    model = Znanie
    form_class = TableOrQuizCreateEditForm
    template_name = 'drevo/quiz_constructor/quiz_question_answer_create.html'
    success_url = reverse_lazy("quiz_constructor_tree")

    def dispatch(self, request, *args, **kwargs):
        """Проверка перед открытием страницы, является ли пользователь экспертом"""
        expert = get_object_or_404(SpecialPermissions, expert=request.user)
        if not expert:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['type_of_zn'] = 'Тест'
        return kwargs

    def get_context_data(self, **kwargs):
        """Передает контекст в шаблон"""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Создание теста'

        # Передаем формы для создания знания и добавления фотографий к знанию
        if self.request.POST:
            context['form'] = TableOrQuizCreateEditForm(self.request.POST)
            context['image_form'] = ZnImageFormSet(self.request.POST)
        else:
            context['form'] = TableOrQuizCreateEditForm(user=self.request.user, type_of_zn='Тест')
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
            return render(request, 'drevo/quiz_constructor/quiz_question_answer_create.html', {
                'form': form,
                'new_znanie_name': knowledge.name,
                'new_znanie_id': knowledge.id,
                'new': True,
                'type_of_zn': 'test',
            })

        return self.form_invalid(form, image_form)

    def form_invalid(self, form, image_form):
        return self.render_to_response(self.get_context_data(form=form, image_form=image_form))


class QuizEditView(LoginRequiredMixin, UpdateView):
    """Представление редактирования знания вида Тест"""
    model = Znanie
    form_class = TableOrQuizCreateEditForm
    template_name = 'drevo/quiz_constructor/quiz_question_answer_edit.html'
    success_url = reverse_lazy("quiz_constructor_tree")

    def dispatch(self, request, *args, **kwargs):
        """Проверка перед открытием страницы, является ли пользователь экспертом"""
        expert = get_object_or_404(SpecialPermissions, expert=request.user)
        if not expert:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['type_of_zn'] = 'Тест'
        return kwargs

    def get_context_data(self, **kwargs):
        """Передает контекст в шаблон"""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактирование теста'
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

            return render(request, 'drevo/quiz_constructor/quiz_question_answer_edit.html', {
                'form': form,
                'changed_znanie_name': knowledge.name,
                'changed_znanie_id': knowledge.id,
                'new': True,
                'type_of_zn': 'test',
            })

        return self.form_invalid(form, image_form)

    def form_invalid(self, form, image_form):
        return self.render_to_response(self.get_context_data(form=form, image_form=image_form))


class AnswerOrQuestionCreateView(LoginRequiredMixin, CreateView):
    """Представление создания знания - вопроса или ответа"""
    model = Znanie
    template_name = 'drevo/quiz_constructor/quiz_question_answer_create.html'
    success_url = reverse_lazy("quiz_constructor_tree")

    def get_form_class(self, **kwargs):
        if self.kwargs.get('type_of_zn') == 'question':
            return QuestionToQuizCreateForm
        else:
            return AnswerToQuizCreateForm

    def dispatch(self, request, *args, **kwargs):
        """Проверка перед открытием страницы, является ли пользователь экспертом"""
        expert = get_object_or_404(SpecialPermissions, expert=request.user)
        if not expert:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Передает контекст в шаблон"""
        context = super().get_context_data(**kwargs)
        type_of_zn = self.kwargs.get('type_of_zn')
        if type_of_zn == 'question':
            context['title'] = 'Создание вопроса теста'
        else:
            context['title'] = 'Создание ответа теста'
        # Передаем формы для создания знания
        if self.request.POST:
            if type_of_zn == 'question':
                context['form'] = QuestionToQuizCreateForm(self.request.POST)
            else:
                context['form'] = AnswerToQuizCreateForm(self.request.POST)
        else:
            if type_of_zn == 'question':
                context['form'] = QuestionToQuizCreateForm()
            else:
                context['form'] = AnswerToQuizCreateForm()

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
            return render(request, 'drevo/quiz_constructor/quiz_question_answer_create.html', {
                'form': form,
                'new': True,
                'new_znanie_name': knowledge.name,
                'new_znanie_id': knowledge.id,
                'type_of_zn': self.kwargs.get('type_of_zn'),
            })
        return self.form_invalid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


class AnswerOrQuestionEditView(LoginRequiredMixin, UpdateView):
    """Представление страницы изменения вопроса или ответа теста"""
    model = Znanie
    form_class = NameOfZnanieCreateUpdateForm
    template_name = 'drevo/quiz_constructor/quiz_question_answer_edit.html'
    success_url = reverse_lazy("quiz_constructor_tree")

    def dispatch(self, request, *args, **kwargs):
        """Проверка перед открытием страницы, является ли пользователь экспертом"""
        expert = get_object_or_404(SpecialPermissions, expert=request.user)
        if not expert:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Передает контекст в шаблон"""
        context = super().get_context_data(**kwargs)
        if self.kwargs.get('type_of_zn') == 'question':
            context['title'] = 'Редактирование вопроса теста'
        else:
            context['title'] = 'Редактирование ответа на вопрос теста'
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
            return render(request, 'drevo/quiz_constructor/quiz_question_answer_edit.html', {
                'form': form,
                'changed_znanie_name': knowledge.name,
                'changed_znanie_id': knowledge.id,
                'new': True,
                'type_of_zn': self.kwargs.get('type_of_zn'),
            })
        return self.form_invalid(form)


def delete_answer_in_quiz(answer_id):
    """Удаление ответа в тесте. В таком случае удаляются связь с вопросом и сам ответ"""
    Relation.objects.filter(rz_id=answer_id).delete()
    Znanie.objects.filter(id=answer_id).delete()


def delete_answers_or_questions_to_quiz(request):
    """Удаление вопроса/ответа теста"""
    data = json.loads(request.body)
    if data['type_of_zn'] == 'answer':
        # Удаление ответа в тесте
        answer_id = data['id']
        delete_answer_in_quiz(answer_id)
    else:
        # Удаление вопроса в тесте. В таком случае удаляются связи с ответом и самим тестом; знание «Вопрос» и «Ответ»
        question_id = data['id']
        Relation.objects.filter(rz_id=question_id).delete()
        relations_with_answers = Relation.objects.filter(bz_id=question_id)
        for relation in relations_with_answers:
            delete_answer_in_quiz(relation.rz_id)

        get_object_or_404(Znanie, id=question_id).delete()

    return JsonResponse({})


def delete_quiz(request):
    """Удаление теста. В таком случае удаляются связи вида «Тест», с вопросами и ответами на вопросы теста;
    знания «Вопрос» и «Ответ»"""
    data = json.loads(request.body)
    quiz_id = data['id']

    # Удаление просмотра теста при его существовании (protect-объект)
    BrowsingHistory.objects.filter(znanie_id=quiz_id).delete()

    # Удаление связи вида "Тест", где связанным знанием является выбранный тест
    Relation.objects.filter(rz_id=quiz_id).delete()

    relations_with_questions = Relation.objects.filter(bz_id=quiz_id)
    for relation_with_question in relations_with_questions:
        relations_with_answers = Relation.objects.filter(bz_id=relation_with_question.rz_id)
        for relation_with_answers in relations_with_answers:
            delete_answer_in_quiz(relation_with_answers.rz_id)
        relation_with_question.delete()
        get_object_or_404(Znanie, rz_id=relation_with_question.rz_id).delete()

    get_object_or_404(Znanie, id=quiz_id).delete()

    return JsonResponse({})


def get_answers_to_selected_question_of_quiz(request):
    """Получение ответов на выбранный вопрос теста"""
    data = json.loads(request.body)
    question_id = data['id']
    selected_answers = Relation.objects.filter(bz_id=question_id)
    answers_attributes = selected_answers.values('rz_id', 'rz__name', 'tr__name').order_by('rz__name')
    return JsonResponse(list(answers_attributes), safe=False)


def get_form_data_for_quiz_constructor(request):
    """
    Получение данных формы и создание трех связей таблицы, строки, столбца и значения при условии,
    что заполнены все поля
    """
    # Нахождение id связей с именами "Тест" и "Состав", "Ответ верный", "Ответ неверный"
    structure_relation_id = get_object_or_404(Tr, name='Состав').id
    correct_answer_id = get_object_or_404(Tr, name='Ответ верный').id
    incorrect_answer_id = get_object_or_404(Tr, name='Ответ неверный').id

    # Получение значений выбранного теста
    selected_test_pk = request.POST.get('test')
    selected_question_pk = request.POST.get('question')

    # Создание связи "Состав": базовое знание - выбранный тест, связанное знание - выбранный вопрос
    create_relation(selected_test_pk, selected_question_pk, structure_relation_id, request)

    for key in request.POST.keys():
        # Если пользователь изменил ответ как верный или неверный, меняется соответствующий объект
        if key.startswith('existing_answer_'):
            answer_id = request.POST.get(key)
            is_correct_answer = request.POST.get(f"is_correct_answer_{answer_id}")
            is_correct_answer = True if is_correct_answer else False
            existing_relation = Relation.objects.get(bz_id=selected_question_pk, rz_id=answer_id)
            is_correct_existing = True if existing_relation.tr_id == correct_answer_id else False
            if is_correct_existing != is_correct_answer:
                if is_correct_answer:
                    existing_relation.tr_id = correct_answer_id
                else:
                    existing_relation.tr_id = incorrect_answer_id
                existing_relation.save()

        elif key.startswith('created_answer_'):
            answer_id = request.POST.get(key)
            is_correct_answer = request.POST.get(f"is_correct_created_answer_{answer_id}")
            is_correct_answer = True if is_correct_answer else False
            if is_correct_answer:
                # Создание связи "Ответ верный": базовое знание - выбранный вопрос, связанное знание - созданный ответ
                create_relation(selected_question_pk, answer_id, correct_answer_id, request)
            else:
                # Создание связи "Ответ неверный": базовое знание - выбранный вопрос, связанное знание - созданный ответ
                create_relation(selected_question_pk, answer_id, incorrect_answer_id, request)

    return JsonResponse({})
