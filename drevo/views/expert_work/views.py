import datetime

from django import forms
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.views.decorators.http import require_http_methods
from django.views.generic import TemplateView

from drevo import models as orm
from drevo.views.expert_work.data_loaders import (
    Question,
    ExpertProposal,
    AnswerProposal,
    load_interview,
)


class QuestionExpertWorkPage(TemplateView):
    """
    Работа эксперта по конкретному вопросу интервью.
    Формируем страницу с:
    - базовой информацией по интервью и вопросу
    - со всеми опубликованными ответами на этот вопрос
    - со всеми вариантами предложений текущего (request.user.expert) эксперта для каждого варианта ответа
    - со всеми новыми ответами, которые создал эксперт

    """

    template_name = "drevo/expert_work_page/question_expertises.html"

    def get_context_data(self, interview_pk: int, question_pk=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Экспертиза"
        if context.get("new_answer_form") is None:
            context["new_answer_form"] = NewAnswerFromExpertForm()

        context["interview"] = load_interview(interview_pk)

        if question_pk is None:
            return context

        question_raw = get_object_or_404(orm.Znanie, pk=question_pk)

        answers_links = question_raw.base.filter(
            tr_id=orm.Tr.objects.get(name="Ответ [ы]").id
        ).select_related("rz")
        # забираем все ответы по вопросу
        # затем - все предложения в вопросе и в памяти выполняем объединение двух списков:
        # Answer(text = proposal.new_answer_text or proposal.answer.name)
        answer_proposals = []
        for answer_link in answers_links:
            answer = answer_link.rz
            answer_proposals.append(
                ExpertProposal(
                    id=answer.pk,
                    is_agreed=False,
                    is_incorrect_answer=False,
                    updated=datetime.datetime.now(),
                    text=answer.name,
                )
            )

        proposals = orm.InterviewAnswerExpertProposal.objects.filter(
            answer_id=None, interview_id=interview_pk, question_id=question_pk
        )
        for p in proposals:
            # предложение к существующему вопросу
            if p.answer is not None:
                exist_prop = answer_proposals[p.answer.pk]
                exist_prop.is_incorrect_answer = p.is_incorrect_answer
                exist_prop.is_agreed = p.is_agreed
                exist_prop.updated = p.updated
            else:
                answer_proposals.append(
                    ExpertProposal(
                        id=0,
                        text=p.new_answer_text,
                        is_agreed=p.is_agreed,
                        is_incorrect_answer=p.is_incorrect_answer,
                        updated=p.updated,
                    )
                )

        context["answer_proposals"] = answer_proposals

        context["question"] = Question(id=question_pk, title=question_raw.name)
        return context


class NewAnswerFromExpertForm(forms.Form):
    text = forms.CharField(max_length=5)
    comment = forms.JSONField(required=False)


@require_http_methods(["POST"])
def post_new_answer(req: HttpRequest, interview_pk: int, question_pk: int, **kwargs):
    # TODO: шаблон для ответа с мнением
    form = NewAnswerFromExpertForm(req.POST)
    context = {}
    if form.is_valid():
        status = 201
        new_proposal_raw = orm.InterviewAnswerExpertProposal.create_new_proposal(
            expert_user=req.user,
            interview_id=interview_pk,
            question_id=question_pk,
            **form.cleaned_data
        )

        context["interview"] = dict(id=interview_pk)
        context["question"] = dict(id=question_pk)
        context["answer"] = AnswerProposal(
            id=0,
            text=form.cleaned_data["text"],
            is_agreed=new_proposal_raw.is_agreed,
            is_incorrect_answer=new_proposal_raw.is_incorrect_answer,
        )
        context["form"] = form
    else:
        status = 400

    return TemplateResponse(
        req, "drevo/expert_work_page/answer_block.html", context, status=status
    )


class AnswerProposalForm(forms.Form):
    is_agreed = forms.BooleanField()
    is_incorrect_answer = forms.BooleanField()


@require_http_methods(["POST"])
def post_answer_proposal(req: HttpRequest, interview_pk: int, answer_pk: int):
    """
    Добавление мнения к определенному ответу.
    """
    # TODO: Сделать вьюху для запросов на обновление мнения эксперта
    # TODO: Нужен отдельный шаблон для этой части. Его же здесь и вернем
    form = AnswerProposalForm(req.POST)
    if form.is_valid():
        prop = orm.InterviewAnswerExpertProposal.get_actual_proposal(
            req.user.pk, answer_pk, interview_pk
        )
        prop.is_agreed = form.cleaned_data.is_agreed
        prop.is_incorrect_answer = form.cleaned_data.is_incorrect_answer
        prop.save()
    # TODO: добавить в шаблон proposal_form.html отображение ошибок формы
    context = dict(
        answer=dict(id=answer_pk, proposal=form.cleaned_data),
        interview=dict(id=interview_pk),
        form=form,
    )

    return TemplateResponse(
        req, "drevo/expert_work_page/proposal_form.html", context=context
    )
