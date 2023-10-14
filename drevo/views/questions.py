from drevo.forms.answer_form import FormAnswer
from django.db import models
from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect
from drevo.models import (
    UserAnswerToQuestion, 
    QuestionToKnowledge,
    Znanie
)


def save_answer(request, pk):
    if request.method == "POST":
        form = FormAnswer(request.POST, request.FILES)
        question_id = request.POST.get("question_id")
        if form.is_valid():
            answer = form.cleaned_data["answer"]
            file = request.FILES["file"]
            UserAnswerToQuestion(
                knowledge = Znanie.objects.get(id=pk),
                question = QuestionToKnowledge.objects.get(id=question_id),
                answer = answer,
                answer_file = file,
                user = request.user
            ).save()
            return HttpResponseRedirect("questions_user")
    knowledge = Znanie.objects.get(id=pk).name
    questions = QuestionToKnowledge.objects.filter(knowledge=pk)
    return render(request, "drevo/questions_user.html",{
        "pk": pk,
        "znanie": knowledge,
        "questions": questions,
        "answer": FormAnswer
    })


def show_questions(request, pk):
    knowledge = Znanie.objects.get(id=pk).name
    questions = QuestionToKnowledge.objects.filter(knowledge=pk)
    return render(request, "drevo/show_questions.html",{
        "pk": pk,
        "znanie": knowledge,
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
                        check_answer.save()
                    elif data[every_object] == "not_accepted":
                        check_answer.accepted = False
                        check_answer.inspector = request.user
                        check_answer.save()  
                    else:
                        check_answer.accepted = False
                        check_answer.inspector = None
                        check_answer.save() 
        return HttpResponseRedirect('answers_from_users')

    question = QuestionToKnowledge.objects.get(id=question_id)
    return render(request, "drevo/answers_from_users.html",{
        "question": question,
        "answers": answers
    })
    
