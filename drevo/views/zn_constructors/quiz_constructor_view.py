import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.generic import CreateView, TemplateView, UpdateView

from drevo.forms.constructor_knowledge_form import (AttributesOfZnForm, QuestionToQuizCreateForm, AnswerToQuizCreateForm, AttributesOfAnswerForm)
from drevo.models import BrowsingHistory, Znanie, Relation, Tr

from .mixins import DispatchMixin
from .supplementary_functions import create_zn_for_constructor, create_relation


class QuizConstructorView(LoginRequiredMixin, TemplateView, DispatchMixin):
    """
    Отображение страницы "Конструктор тестов"
    """
    template_name = 'drevo/quiz_constructor/quiz_constructor.html'

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


class AnswerOrQuestionCreateView(LoginRequiredMixin, CreateView, DispatchMixin):
    """Представление создания знания - вопроса или ответа"""
    model = Znanie
    template_name = 'drevo/quiz_constructor/quiz_question_answer_create.html'

    def __init__(self):
        super().__init__()
        self.zn_create_form = None
        self.zn_attr_form = None
        self.type_of_zn = None
        self.parent_id = None

    def get_form_class(self):
        self.type_of_zn = self.kwargs.get('type_of_zn')
        if self.type_of_zn == 'question':
            return QuestionToQuizCreateForm
        else:
            return AnswerToQuizCreateForm

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
            context['zn_create_form'] = self.zn_create_form(self.request.POST)
            context['zn_attr_form'] = self.zn_attr_form(self.request.POST)
        else:
            context['zn_create_form'] = self.zn_create_form()
            context['zn_attr_form'] = self.zn_attr_form()

        return context

    def get(self, request, *args, **kwargs):
        """Обрабатывает GET запрос"""
        self.object = None
        type_of_zn = self.kwargs.get('type_of_zn')
        if type_of_zn == 'question':
            self.zn_create_form = QuestionToQuizCreateForm
            self.zn_attr_form = AttributesOfZnForm
        else:
            self.zn_create_form = AnswerToQuizCreateForm
            self.zn_attr_form = AttributesOfAnswerForm

        form_class = self.get_form_class()
        zn_create_form = self.get_form(form_class)
        zn_attr_form = self.zn_attr_form()
        return self.render_to_response(self.get_context_data(zn_create_form=zn_create_form, zn_attr_form=zn_attr_form))

    def post(self, request, *args, **kwargs):
        """Обрабатывает POST запрос"""
        self.object = None
        # Получаем форму для заполнения данных Знания
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        self.type_of_zn = self.kwargs.get('type_of_zn')
        if self.type_of_zn == 'answer':
            zn_attr_form = AttributesOfAnswerForm(self.request.POST)
        else:
            zn_attr_form = AttributesOfZnForm(self.request.POST)
        if form.is_valid() and zn_attr_form.is_valid():
            self.parent_id = self.kwargs.get('parent_id')
            order_of_relation = zn_attr_form.cleaned_data['order_of_relation']
            knowledge = form.save(commit=False)
            create_zn_for_constructor(knowledge, form, request)
            if self.type_of_zn == 'answer':
                is_correct_answer_value = zn_attr_form.cleaned_data['is_correct']
                if is_correct_answer_value:
                    is_correct_answer_tr_id = get_object_or_404(Tr, name='Ответ верный').id
                    create_relation(
                        self.parent_id, knowledge.id, is_correct_answer_tr_id, request, order_of_relation, True
                    )
                else:
                    is_incorrect_answer_tr_id = get_object_or_404(Tr, name='Ответ неверный').id
                    create_relation(
                        self.parent_id, knowledge.id, is_incorrect_answer_tr_id, request, order_of_relation,True)
            else:
                structure_kind_id = get_object_or_404(Tr, name='Состав').id
                create_relation(
                    self.parent_id, knowledge.id, structure_kind_id, request, order_of_relation
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


class AnswerOrQuestionEditView(LoginRequiredMixin, UpdateView, DispatchMixin):
    """Представление страницы изменения вопроса или ответа теста"""
    model = Znanie
    template_name = 'drevo/quiz_constructor/quiz_question_answer_edit.html'

    def __init__(self):
        super().__init__()
        self.zn_create_form = None
        self.zn_attr_form = None
        self.type_of_zn = None
        self.parent_id = None

    def get_form_class(self):
        self.type_of_zn = self.kwargs.get('type_of_zn')
        if self.type_of_zn == 'question':
            return QuestionToQuizCreateForm
        else:
            return AnswerToQuizCreateForm

    def get(self, request, *args, **kwargs):
        """Обрабатывает GET запрос"""
        self.object = self.get_object()
        type_of_zn = self.kwargs.get('type_of_zn')
        order_of_relation = Relation.objects.filter(rz_id=self.kwargs.get('pk')).first().order
        if type_of_zn == 'question':
            self.zn_edit_form = QuestionToQuizCreateForm
            self.zn_attr_form = AttributesOfZnForm
        else:
            self.zn_edit_form = AnswerToQuizCreateForm
            self.zn_attr_form = AttributesOfAnswerForm

        form_class = self.get_form_class()
        zn_edit_form = self.get_form(form_class)
        zn_attr_form = self.zn_attr_form(initial={'order_of_relation': order_of_relation})
        return self.render_to_response(self.get_context_data(zn_edit_form=zn_edit_form, zn_attr_form=zn_attr_form))

    def get_context_data(self, **kwargs):
        """Передает контекст в шаблон"""
        context = super().get_context_data(**kwargs)
        if self.kwargs.get('type_of_zn') == 'question':
            context['title'] = 'Редактирование вопроса теста'
        else:
            context['title'] = 'Редактирование ответа на вопрос теста'
        context['pk'] = self.kwargs.get('pk')
        return context


    def post(self, request, *args, **kwargs):
        """Обрабатывает POST запрос"""
        self.object = self.get_object()
        # Получаем форму для заполнения данных Знания
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        self.type_of_zn = self.kwargs.get('type_of_zn')
        if self.type_of_zn == 'answer':
            zn_attr_form = AttributesOfAnswerForm(self.request.POST)
        else:
            zn_attr_form = AttributesOfZnForm(self.request.POST)
        if form.is_valid() and zn_attr_form.is_valid():
            self.parent_id = self.kwargs.get('parent_id')
            order_of_relation = zn_attr_form.cleaned_data['order_of_relation']
            knowledge = form.save(commit=False)
            create_zn_for_constructor(knowledge, form, request)
            if self.type_of_zn == 'answer':
                is_correct_answer_value = zn_attr_form.cleaned_data['is_correct']
                if is_correct_answer_value:
                    is_correct_answer_tr_id = get_object_or_404(Tr, name='Ответ верный').id
                    create_relation(
                        self.parent_id, knowledge.id, is_correct_answer_tr_id, request, order_of_relation, True
                    )
                else:
                    is_incorrect_answer_tr_id = get_object_or_404(Tr, name='Ответ неверный').id
                    create_relation(
                        self.parent_id, knowledge.id, is_incorrect_answer_tr_id, request, order_of_relation,True)
            else:
                structure_kind_id = get_object_or_404(Tr, name='Состав').id
                create_relation(
                    self.parent_id, knowledge.id, structure_kind_id, request, order_of_relation
                )
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
    знания «Вопрос» и «Ответ», знание «Тест»"""
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
        question_id = relation_with_question.rz_id
        relation_with_question.delete()
        get_object_or_404(Znanie, rz_id=question_id).delete()

    get_object_or_404(Znanie, id=quiz_id).delete()

    return JsonResponse({})


def get_answers_to_selected_question_of_quiz(request):
    """Получение ответов на выбранный вопрос теста"""
    data = json.loads(request.body)
    question_id = data['id']
    selected_answers = Relation.objects.filter(bz_id=question_id)
    answers_attributes = selected_answers.values('rz_id', 'rz__name', 'tr__name').order_by('rz__name')
    return JsonResponse(list(answers_attributes), safe=False)


def answers_in_quiz_existence(request):
    """Проверка, есть ли в тесте хотя бы один ответ и есть ли вопросы без ответа"""
    data = json.loads(request.body)
    selected_test_pk = data['id']
    relations_with_question = Relation.objects.filter(bz_id=selected_test_pk, tr__name='Состав')
    questions_less_two_answers = []
    questions_without_correct_answer = []
    for relation in relations_with_question:
        is_relation_with_correct_answer = Relation.objects.filter(bz_id=relation.rz_id, tr__name='Ответ верный')
        is_relation_with_incorrect_answer = Relation.objects.filter(bz_id=relation.rz_id, tr__name='Ответ неверный')
        if (is_relation_with_correct_answer.count() + is_relation_with_incorrect_answer.count()) < 2:
            questions_less_two_answers.append(relation.rz.name)
        if not is_relation_with_correct_answer.exists():
            questions_without_correct_answer.append(relation.rz.name)

    return JsonResponse({'questions_less_two_answers': questions_less_two_answers,
                         'questions_without_correct_answer': questions_without_correct_answer})
