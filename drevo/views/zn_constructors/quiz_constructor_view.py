from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods
from django.views.generic import TemplateView

from drevo.forms.knowledge_create_form import ZnImageFormSet, ZnFilesFormSet
from drevo.forms.constructor_knowledge_form import (OrderOfRelationForm, QuestionToQuizCreateEditForm,
                                                    AnswerToQuizCreateEditForm, AnswerCorrectForm,
                                                    MainZnInConstructorCreateEditForm)
from drevo.models import BrowsingHistory, Znanie, Relation, Tr

from .mixins import DispatchMixin
from .supplementary_functions import create_zn_for_constructor, create_relation


class QuizConstructorView(DispatchMixin, TemplateView):
    """
    Отображение страницы "Конструктор тестов"
    """
    template_name = 'drevo/constructors/quiz_constructor.html'

    def get_context_data(self, **kwargs):
        """Передает контекст в шаблон"""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Конструктор тестов'
        pk = self.kwargs.get('pk')
        selected_quiz = Znanie.objects.get(id=pk)
        context["main_zn_name"] = selected_quiz.name
        context["main_zn_id"] = selected_quiz.id

        selected_questions = Relation.objects.filter(bz_id=pk, tr__name="Состав")
        questions_attributes = selected_questions.values('rz_id', 'rz__name').order_by('rz__name')
        if questions_attributes:
            context["questions_attributes"] = questions_attributes

        main_zn_edit_form = MainZnInConstructorCreateEditForm(instance=selected_quiz,
                                                              user=self.request.user,
                                                              type_of_zn='test')
        context['main_zn_edit_form'] = main_zn_edit_form
        context['main_zn_edit_form_uuid'] = main_zn_edit_form.fields['content'].widget.attrs['id']
        context['images_form_for_main_zn'] = ZnImageFormSet(instance=selected_quiz)
        context['file_form_for_main_zn'] = ZnFilesFormSet(instance=selected_quiz)

        return context


@require_http_methods(['GET', 'POST'])
def question_create_update_in_quiz(request):
    """Представление для создания/редактирования вопроса теста"""
    if request.method == 'GET':
        # Получение форм для создания знания
        if request.GET.get('action') == 'create':
            zn_form = QuestionToQuizCreateEditForm()
            order_of_rel_form = OrderOfRelationForm()
        # Получение форм для редактирования знания
        else:
            current_zn = get_object_or_404(Znanie, id=request.GET.get('zn_id'))
            zn_form = QuestionToQuizCreateEditForm(instance=current_zn)
            order_of_relation = Relation.objects.filter(rz_id=current_zn.id).first().order
            order_of_rel_form = OrderOfRelationForm(initial={'order_of_relation': order_of_relation})

        return JsonResponse({'zn_form': f'{zn_form.as_p()}', 'order_of_rel_form': f'{order_of_rel_form.as_p()}'})
    else:
        # Сохранение нового/изменённого знания
        req_data = request.POST
        if req_data.get('action') == 'edit':
            form = QuestionToQuizCreateEditForm(data=req_data,
                                                instance=get_object_or_404
                                                (Znanie, id=req_data.get('edited_zn_id')))
        else:
            form = QuestionToQuizCreateEditForm(data=req_data)
        order_of_rel_form = OrderOfRelationForm(req_data)
        if form.is_valid() and order_of_rel_form.is_valid():
            quiz_id = req_data.get('quiz_id')
            order_of_relation = order_of_rel_form.cleaned_data['order_of_relation']
            knowledge = form.save(commit=False)
            create_zn_for_constructor(knowledge, form, request)
            structure_kind_id = get_object_or_404(Tr, name='Состав').id
            create_relation(quiz_id, knowledge.id, structure_kind_id, request, order_of_relation)
            return JsonResponse({'zn_id': knowledge.id, 'zn_name': knowledge.name}, status=200)
        return JsonResponse({}, status=400)


@require_http_methods(['GET', 'POST'])
def answer_create_update_in_quiz(request):
    """Представление для создания/редактирования ответа теста"""
    is_correct_answer_tr_id = get_object_or_404(Tr, name='Ответ верный').id
    if request.method == 'GET':
        # Получение форм для создания знания
        if request.GET.get('action') == 'create':
            zn_form = AnswerToQuizCreateEditForm()
            order_of_rel_form = OrderOfRelationForm()
            answer_correct_form = AnswerCorrectForm()
        # Получение форм для редактирования знания
        else:
            current_zn = get_object_or_404(Znanie, id=request.GET.get('zn_id'))
            zn_form = AnswerToQuizCreateEditForm(instance=current_zn)
            order_of_relation = Relation.objects.filter(rz_id=current_zn.id).first().order
            order_of_rel_form = OrderOfRelationForm(initial={'order_of_relation': order_of_relation})
            if Relation.objects.filter(rz_id=current_zn.id).first().tr_id == is_correct_answer_tr_id:
                answer_correct_form = AnswerCorrectForm(initial={'answer_correct': True})
            else:
                answer_correct_form = AnswerCorrectForm(initial={'answer_correct': False})
        return JsonResponse(
            {'zn_form': f'{zn_form.as_p()}', 'order_of_rel_form': f'{order_of_rel_form.as_p()}',
             'answer_correct_form': f'{answer_correct_form.as_p()}'})
    else:
        # Сохранение нового/изменённого знания
        req_data = request.POST
        if req_data.get('action') == 'edit':
            form = AnswerToQuizCreateEditForm(data=req_data,
                                              instance=get_object_or_404
                                              (Znanie, id=req_data.get('edited_zn_id')))
        else:
            form = AnswerToQuizCreateEditForm(data=req_data)
        order_of_rel_form = OrderOfRelationForm(req_data)
        answer_correct_form = AnswerCorrectForm(req_data)
        if form.is_valid() and order_of_rel_form.is_valid() and answer_correct_form.is_valid():
            question_id = req_data.get('question_id')
            order_of_relation = order_of_rel_form.cleaned_data['order_of_relation']
            knowledge = form.save(commit=False)
            create_zn_for_constructor(knowledge, form, request)
            is_correct_answer_value = answer_correct_form.cleaned_data['answer_correct']
            if is_correct_answer_value:
                create_relation(
                    question_id, knowledge.id, is_correct_answer_tr_id, request, order_of_relation, True
                )
            else:
                is_incorrect_answer_tr_id = get_object_or_404(Tr, name='Ответ неверный').id
                create_relation(
                    question_id, knowledge.id, is_incorrect_answer_tr_id, request, order_of_relation, True)
            return JsonResponse({'zn_id': knowledge.id, 'zn_name': knowledge.name}, status=200)
        return JsonResponse({}, status=400)


def delete_answer_in_quiz(answer_id):
    """Удаление ответа в тесте. В таком случае удаляются связь с вопросом и сам ответ"""
    Relation.objects.filter(rz_id=answer_id).delete()
    Znanie.objects.filter(id=answer_id).delete()


def delete_answers_or_questions_to_quiz(request):
    """Удаление вопроса/ответа теста"""
    type_of_zn = request.GET.get('type_of_zn')
    zn_id = request.GET.get('id')
    if type_of_zn == 'answer':
        # Удаление ответа в тесте
        delete_answer_in_quiz(zn_id)
    else:
        # Удаление вопроса в тесте. В таком случае удаляются связи с ответом и самим тестом; знание «Вопрос» и «Ответ»
        Relation.objects.filter(rz_id=zn_id).delete()
        relations_with_answers = Relation.objects.filter(bz_id=zn_id)
        for relation in relations_with_answers:
            delete_answer_in_quiz(relation.rz_id)
        get_object_or_404(Znanie, id=zn_id).delete()

    return HttpResponse(status=200)


def delete_quiz(request):
    """Удаление теста. В таком случае удаляются связи вида «Тест», с вопросами и ответами на вопросы теста;
    знания «Вопрос» и «Ответ», знание «Тест»"""
    quiz_id = request.GET.get('id')

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

    return HttpResponse(status=200)


def get_answers_to_selected_question_of_quiz(request):
    """Получение ответов на выбранный вопрос теста"""
    question_id = request.GET.get('id')
    selected_answers = Relation.objects.filter(bz_id=question_id)
    answers_attributes = selected_answers.values('rz_id', 'rz__name', 'tr__name').order_by('rz__name')
    return JsonResponse(list(answers_attributes), safe=False)


def answers_in_quiz_existence(request):
    """Проверка, возможно ли открыть тест: для этого в каждом вопросе должно быть хотя бы два отевта,
    один из которых верен"""
    selected_test_pk = request.GET.get('id')
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
