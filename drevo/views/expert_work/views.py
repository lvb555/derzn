from django import forms
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.views.decorators.http import require_http_methods
from django.views.generic import TemplateView
from drevo import models as orm
from drevo.views.expert_work.data_loaders import load_interview


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

    def get_context_data(self, interview_pk: int, question_pk, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Экспертиза"
        if context.get("new_answer_form") is None:
            context["new_answer_form"] = NewAnswerFromExpertForm()
        context["interview"] = load_interview(interview_pk)

        # забираем все ответы по вопросу
        question_raw = get_object_or_404(orm.Znanie, pk=question_pk)
        answers_links = question_raw.base.filter(
            tr_id=orm.Tr.objects.get(name="Ответ [ы]").id
        ).select_related("rz")

        answers = {}
        for answer_link in answers_links:
            answer = answer_link.rz
            answers[answer.pk] = dict(
                id=answer.pk,
                text=answer.name,
            )

        # собираем предложения
        proposals = orm.InterviewAnswerExpertProposal.objects.filter(
            interview_id=interview_pk,
            question_id=question_pk,
            expert_id=self.request.user.pk,
        ).order_by("id")

        # и если оно имеет привязку к ответу - присоединяем к нему.
        # В остальных случаях - это список новых предложенных ответов от эксперта
        proposed_answers = []
        for p in proposals:
            # предложение к существующему вопросу
            if p.answer is not None:
                exist_prop = answers[p.answer.pk]
                exist_prop["proposal"] = p
            else:
                proposed_answers.append(p)

        context["answers"] = answers.values()
        context["proposed_answers"] = proposed_answers
        context["question"] = dict(id=question_pk, title=question_raw.name)
        return context


class NewAnswerFromExpertForm(forms.Form):
    text = forms.CharField()
    is_agreed = forms.BooleanField(required=False)
    is_incorrect_answer = forms.BooleanField(required=False)
    comment = forms.JSONField(required=False)


@require_http_methods(["POST"])
def propose_answer(req: HttpRequest, interview_pk: int, question_pk: int, **kwargs):
    """
    Эксперт предлагает новый ответ в качестве предложения
    """
    form = NewAnswerFromExpertForm(req.POST)
    context = dict(interview=dict(id=interview_pk), question=dict(id=question_pk))

    if form.is_valid():
        status = 201
        context["proposal"] = orm.InterviewAnswerExpertProposal.create_new_proposal(
            expert_user=req.user,
            interview_id=interview_pk,
            question_id=question_pk,
            **form.cleaned_data,
        )
    else:
        status = 400

    context["form"] = form
    return TemplateResponse(
        req, "drevo/expert_work_page/proposed_answer_block.html", context, status=status
    )


class AnswerProposalForm(forms.Form):
    is_agreed = forms.BooleanField(required=False)
    is_incorrect_answer = forms.BooleanField(required=False)
    answer_pk = forms.IntegerField(required=False)
    proposal_pk = forms.IntegerField(required=False)


@require_http_methods(["POST"])
def update_answer_proposal(
    req: HttpRequest, interview_pk: int, question_pk: int, answer_pk: int
):
    """
    Добавление/обновление мнения к определенному ответу.
    """

    form = AnswerProposalForm(req.POST)
    if form.is_valid():
        proposal_pk = form.cleaned_data.get("proposal_pk")
        if proposal_pk:
            prop = orm.InterviewAnswerExpertProposal.objects.get(id=proposal_pk)

            form.cleaned_data["id"] = form.cleaned_data.pop("proposal_pk")
        else:
            prop, _ = orm.InterviewAnswerExpertProposal.objects.get_or_create(
                expert=req.user,
                interview_id=interview_pk,
                answer_id=answer_pk,
                question_id=question_pk,
            )
            form.cleaned_data.pop("proposal_pk")
            form.cleaned_data["id"] = prop.pk

        prop.is_agreed = form.cleaned_data.get("is_agreed", False)
        prop.is_incorrect_answer = form.cleaned_data.get("is_incorrect_answer", False)
        prop.save()

    proposal_data = form.cleaned_data
    answer_pk = proposal_data.pop("answer_pk", None)
    context = dict(
        answer=dict(id=answer_pk),
        interview=dict(id=interview_pk),
        question=dict(id=question_pk),
        proposal=proposal_data,
        form=form,
    )

    return TemplateResponse(
        req, "drevo/expert_work_page/proposal_form_body.html", context=context
    )


@require_http_methods(["POST"])
def update_proposed_answer(req: HttpRequest, proposal_pk: int):
    """
    Метод обновления предложенного ответа
    """
    form = AnswerProposalForm(req.POST)
    prop = orm.InterviewAnswerExpertProposal.objects.get(id=proposal_pk)
    context = dict(
        answer=prop.answer,
        interview=dict(id=prop.interview.pk),
        question=dict(id=prop.question.pk),
        form=form,
        proposal=prop,
    )
    if form.is_valid():
        form_data = form.cleaned_data
        prop.is_agreed = form_data.get("is_agreed", False)
        prop.is_incorrect_answer = form_data.get("is_incorrect_answer", False)
        prop.save()
        form_data["id"] = form_data.pop("proposal_pk", None)

    return TemplateResponse(
        req, "drevo/expert_work_page/proposed_answer_block.html", context=context
    )
