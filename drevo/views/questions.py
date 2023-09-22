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
            return HttpResponseRedirect("questions")
    knowledge = Znanie.objects.get(id=pk).name
    questions = QuestionToKnowledge.objects.filter(knowledge=pk)
    return render(request, "drevo/questions.html",{
        "pk": pk,
        "znanie": knowledge,
        "questions": questions,
        "answer": FormAnswer
    })