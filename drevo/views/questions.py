import json
from django.db import models
from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from drevo.models.refuse_reason import RefuseReason
from drevo.models import (
    UserAnswerToQuestion, 
    QuestionToKnowledge,
    Znanie
)


@login_required
def save_answer(request, pk):

    if request.method == "GET":
        knowledge = Znanie.objects.get(id=pk)
        questions = QuestionToKnowledge.objects.filter(knowledge=pk)
        answers = UserAnswerToQuestion.objects.filter(knowledge=pk, user=request.user)
        return render(request, "drevo/questions_user.html",{
            "pk": pk,
            "znanie": knowledge,
            "questions": questions,
            "answers": answers
        })

    elif request.method == "PUT":
        data = json.loads(request.body)
        answer_id = data.get("answer")
        editable_answer = UserAnswerToQuestion.objects.get(id=answer_id)
        if data.get("operation") == "delete_answer":
            editable_answer.answer_file.delete(save=True)
            editable_answer.delete()
            return HttpResponse(status=200)
        elif data.get("operation") == "delete_file":
            editable_answer.answer_file.delete(save=True)
            return HttpResponse(status=200)
        elif data.get("operation") == "delete_text":
            editable_answer.answer = '-'
            editable_answer.save()           
            return HttpResponse(status=200)
        elif data.get("operation") == "edit_text":
            new_text_answer = data.get("new_text")
            editable_answer.answer = new_text_answer
            editable_answer.save()
            return HttpResponse(status=200)
        elif data.get("operation") == "add_text":
            text_answer = data.get("text_answer")
            editable_answer.answer = text_answer
            editable_answer.save()
            return HttpResponse(status=200)
                 
    elif request.method == "POST":
        # добавление файла
        if  request.POST.get("operation") == "add_file":
            answer_id = request.POST.get("answer_id")
            file = request.FILES["new_file"]
            editable_answer = UserAnswerToQuestion.objects.get(id=answer_id)
            editable_answer.answer_file.delete(save=True)
            editable_answer.answer_file = file
            editable_answer.save()
            return HttpResponse(status=200)
        # новый ответ
        elif request.POST.get("question_id"):
            question_id = request.POST.get("question_id")
            answer_to_question = UserAnswerToQuestion()

            answer_to_question.user = request.user
            answer_to_question.knowledge = Znanie.objects.get(id=pk)
            answer_to_question.question = QuestionToKnowledge.objects.get(id=question_id)
            if request.POST.get("text"):
                answer_to_question.answer = request.POST.get("text")
            else:
                answer_to_question.answer = "-"
            if request.FILES:
                answer_to_question.answer_file = request.FILES["file"]
            answer_to_question.save()
            return HttpResponse(status=200)
                

@login_required
def questions_and_check_answers(request, pk):

    if request.method == "POST":
        answers = UserAnswerToQuestion.objects.filter(question_id=request.POST.get("question_id"))
        data = request.POST
        for answer in answers:
            for every_object in data:
                if str(answer.id) == every_object:
                    check_answer = UserAnswerToQuestion.objects.get(id=answer.id)
                    if data[every_object] == "accepted":
                        check_answer.accepted = True
                        check_answer.inspector = request.user
                        check_answer.refuse_reason = None
                        check_answer.save()
                    elif data[every_object] == "not_accepted":
                        check_answer.accepted = False
                        check_answer.inspector = request.user
                        if data['reason' + every_object] and data['reason' + every_object] != 'less':
                            check_answer.refuse_reason = RefuseReason.objects.get(id=data['reason' + every_object])
                        elif data['reason' + every_object] == 'less':
                            check_answer.refuse_reason = None
                        check_answer.save()  
                    else:
                        check_answer.accepted = False
                        check_answer.inspector = None
                        check_answer.refuse_reason = None
                        check_answer.save() 
        return HttpResponseRedirect('questions_and_check_answers')

    answers = UserAnswerToQuestion.objects.filter(knowledge=pk)
    reasons = RefuseReason.objects.all()
    knowledge_name = Znanie.objects.get(id=pk).name
    questions_from_base = QuestionToKnowledge.objects.filter(knowledge=pk, publication=True).order_by('order')
    questions_for_page = []
    for question in questions_from_base:
        for answer in answers:
            if answer.question == question:
                questions_for_page.append(question)
                break
    return render(request, "drevo/questions_and_check_answers.html",{
        "pk": pk,
        "znanie": knowledge_name,
        "questions": questions_for_page,
        "answers": answers,
        "reasons": reasons
    })