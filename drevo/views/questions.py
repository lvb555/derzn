from django.db import models
from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect
from drevo.models.refuse_reason import RefuseReason
from drevo.models import (
    UserAnswerToQuestion, 
    QuestionToKnowledge,
    Znanie
)


def save_answer(request, pk):
    if request.method == "POST":
        if request.POST.get("answer") and request.FILES:
            question_id = request.POST.get("question_id")
            answer = request.POST.get("answer")
            file = request.FILES["file"]
            UserAnswerToQuestion(
                knowledge = Znanie.objects.get(id=pk),
                question = QuestionToKnowledge.objects.get(id=question_id),
                answer = answer,
                answer_file = file,
                user = request.user
            ).save()
        elif request.FILES and not request.POST.get("answer"):
            question_id = request.POST.get("question_id")
            file = request.FILES["file"]
            UserAnswerToQuestion(
                knowledge = Znanie.objects.get(id=pk),
                question = QuestionToKnowledge.objects.get(id=question_id),
                answer = "-",
                answer_file = file,
                user = request.user
            ).save()
        elif request.POST.get("answer") and not request.FILES:
            question_id = request.POST.get("question_id")
            answer = request.POST.get("answer")
            UserAnswerToQuestion(
                knowledge = Znanie.objects.get(id=pk),
                question = QuestionToKnowledge.objects.get(id=question_id),
                answer = answer,
                user = request.user
            ).save()
     
        return HttpResponseRedirect("questions_user")

    knowledge_name = Znanie.objects.get(id=pk).name
    questions = QuestionToKnowledge.objects.filter(knowledge=pk)
    return render(request, "drevo/questions_user.html",{
        "pk": pk,
        "znanie": knowledge_name,
        "questions": questions
    })


def show_questions(request, pk):
    knowledge_name = Znanie.objects.get(id=pk).name
    questions = QuestionToKnowledge.objects.filter(knowledge=pk)
    return render(request, "drevo/show_questions.html",{
        "pk": pk,
        "znanie": knowledge_name,
        "questions": questions
    })


def acceptance(request, pk, question_id):
    answers = UserAnswerToQuestion.objects.filter(question_id=question_id)

    if request.method == "POST":
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
        return HttpResponseRedirect('answers_from_users')

    question = QuestionToKnowledge.objects.get(id=question_id)
    reasons = RefuseReason.objects.all()
    return render(request, "drevo/answers_from_users.html",{
        "question": question,
        "answers": answers,
        "reasons": reasons
    })
    
