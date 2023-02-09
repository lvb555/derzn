from django.http import HttpRequest
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.views.generic import TemplateView, RedirectView

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

    template_name = "drevo/expert_work_page/expert_work_page.html"

    def get_prev_next_question_url(self, cur_question: orm.Znanie) -> tuple[str, str]:
        """
            Метод для получения url предыдущего и следующего вопроса интервью
        """
        prev_url, next_url = None, None
        interview_pk = self.kwargs.get('interview_pk')
        tz_id = orm.Tz.objects.get(name='Вопрос').id
        questions = orm.Znanie.objects.filter(
            tz_id=tz_id, is_published=True, related__bz_id=interview_pk
        ).order_by('-pk')
        prev_quest = questions.filter(pk__lt=cur_question.pk).order_by('-pk')
        if prev_quest.exists():
            prev_pk = prev_quest.first().pk
            prev_url = reverse('question_expert_work', kwargs={'interview_pk': interview_pk, 'question_pk': prev_pk})
        next_quest = questions.filter(pk__gt=cur_question.pk).order_by('pk')
        if next_quest.exists():
            next_pk = next_quest.first().pk
            next_url = reverse('question_expert_work', kwargs={'interview_pk': interview_pk, 'question_pk': next_pk})
        return prev_url, next_url

    def get_context_data(self, interview_pk: int, question_pk, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Экспертиза"
        context["interview"] = load_interview(interview_pk)

        max_agreed = (
            orm.Relation.objects.filter(
                bz_id=question_pk,
                tr_id=orm.Tr.objects.get(name="Число ответов").id,
                #user_id=self.request.user.id
            )
            .order_by()
            .last()
        )
        max_agreed = get_object_or_404(orm.Znanie, id=max_agreed.rz_id).name
        context["max_agreed"] = int(max_agreed)

        # забираем все ответы по вопросу
        question_raw = get_object_or_404(orm.Znanie, pk=question_pk)
        answers_links = question_raw.base.filter(
            tr_id=orm.Tr.objects.get(name="Ответ [ы]").id
        ).select_related("rz").prefetch_related('rz__answ_sub_answers', 'rz__answer_proposals')

        answers = {}
        cur_agreed_count = 0
        for answer_link in answers_links:
            answer = answer_link.rz
            proposal = answer.answer_proposals.all().first()
            if proposal and proposal.is_agreed:
                cur_agreed_count += 1
            answers[answer.pk] = dict(
                id=answer.pk,
                text=answer.name,
                sub_answers=answer.answ_sub_answers.all().values_list('sub_answer', flat=True),
                proposal=proposal
            )
        context['cur_agreed_count'] = cur_agreed_count

        # собираем предложения
        proposals = orm.InterviewAnswerExpertProposal.objects.filter(
            interview_id=interview_pk,
            question_id=question_pk,
            expert_id=self.request.user.pk,
        ).order_by("id")

        # разделяем предложения на две группы,
        # те которе уже прошли проверку администратором 'reviewed' и которые в ожидании 'pending'
        expert_proposals = {'reviewed': list(), 'pending': list()}
        for prop in proposals:
            # предложение к существующему вопросу
            if prop.status:
                expert_proposals['reviewed'].append(prop)
            else:
                expert_proposals['pending'].append(prop)

        prev_quest, next_quest = self.get_prev_next_question_url(cur_question=question_raw)
        context['prev_quest'] = prev_quest
        context['next_quest'] = next_quest

        context["answers"] = answers.values()
        context["expert_proposals"] = expert_proposals
        context["question"] = dict(id=question_pk, title=question_raw.name)

        message_text = self.request.session.get('success_message_text')
        if message_text:
            context['is_saved'] = True
            context['message_text'] = message_text
            del self.request.session['success_message_text']
        return context


@require_http_methods(["POST"])
def propose_answer(req: HttpRequest, interview_pk: int, question_pk: int):
    """
    Эксперт предлагает новый ответ в качестве предложения
    """
    proposal_text = req.POST.get('text')
    proposal_is_agreed = req.POST.get('is_agreed')
    orm.InterviewAnswerExpertProposal.create_new_proposal(
        expert_user=req.user,
        interview_id=interview_pk,
        question_id=question_pk,
        text=proposal_text,
        is_agreed=True if proposal_is_agreed else False,
    )
    message_text = 'Ваше предложение ответа на вопрос было успешно добавлено и ожидает рассмотрения администраниции.'
    req.session['success_message_text'] = message_text
    return redirect(f"{req.META.get('HTTP_REFERER')}#new_answer_text")


@require_http_methods(['POST'])
def sub_answer_create_view(request: HttpRequest, quest_pk: int, answer_pk: int):
    """
        Добавление подответа к ответу на вопрос интервью
    """
    sub_answer = request.POST.get('subanswer')
    question = orm.Znanie.objects.get(pk=quest_pk)
    answer = orm.Znanie.objects.get(pk=answer_pk)
    orm.SubAnswers.objects.create(expert=request.user, question=question, answer=answer, sub_answer=sub_answer)
    message_text = f'Ваш подответ к ответу "{answer.name}" был успешно создан.'
    request.session['success_message_text'] = message_text
    scroll_to_elm = f'answer_{answer.id}'
    return redirect(f"{request.META.get('HTTP_REFERER')}#{scroll_to_elm}")


class ExpertProposalDeleteView(RedirectView):
    """
        Удаление предложения эксперта по вопросу интервью
    """
    def get_redirect_url(self, *args, **kwargs):
        return f"{self.request.META.get('HTTP_REFERER')}#proposed_answers"

    def get(self, request, *args, **kwargs):
        proposal_pk = request.GET.get('proposal_pk')
        queryset = orm.InterviewAnswerExpertProposal.objects.filter(pk=proposal_pk, expert=request.user)
        if queryset.exists():
            queryset.first().delete()
            message_text = 'Ваше предложение ответа по данному вопросу было успешно удалено.'
            request.session['success_message_text'] = message_text
        return super(ExpertProposalDeleteView, self).get(request, *args, **kwargs)


@require_http_methods(['POST', 'GET'])
def set_answer_as_incorrect(request: HttpRequest, proposal_pk: int):
    """
        Определение предложения (ответа) как некорректное
    """
    proposal = get_object_or_404(orm.InterviewAnswerExpertProposal, pk=proposal_pk)
    if request.method == 'GET':
        proposal.incorrect_answer_explanation = ''
        proposal.is_incorrect_answer = False
        message_text = 'Подтверждение, что вы не считаете данный ответ некорректным было сохранено.'
    else:
        explanation = request.POST.get('explanation').strip()
        proposal.incorrect_answer_explanation = explanation
        proposal.is_incorrect_answer = True
        message_text = 'Подтверждение, что вы считаете данный ответ некорректным было сохранено.'
    request.session['success_message_text'] = message_text
    proposal.save()
    scroll_to_elm = f'answer_{proposal.answer_id}'
    return redirect(f"{request.META.get('HTTP_REFERER')}#{scroll_to_elm}")


@require_http_methods(['GET'])
def set_answer_is_agreed(request: HttpRequest, proposal_pk: int):
    """
        Согласиться с предложением
    """
    proposal = get_object_or_404(orm.InterviewAnswerExpertProposal, pk=proposal_pk)
    proposal.is_agreed = True if request.GET.get('is_agreed') else False
    proposal.save()
    message_text = 'Изменения были сохранены.'
    request.session['success_message_text'] = message_text
    if not proposal.answer_id:
        scroll_to_elm = f'opinion_is_agreed_form{proposal_pk}'
    else:
        scroll_to_elm = f'opinion_is_agreed_form{proposal.answer_id}'
    return redirect(f"{request.META.get('HTTP_REFERER')}#{scroll_to_elm}")


@require_http_methods(['POST'])
def proposal_update_view(request: HttpRequest, proposal_pk: int):
    """
        Обновление текста ответа предложения
    """
    proposal = get_object_or_404(orm.InterviewAnswerExpertProposal, pk=proposal_pk)
    proposal.new_answer_text = request.POST.get('new_proposal_text')
    proposal.save()
    message_text = f'Изменения были сохранены.'
    request.session['success_message_text'] = message_text
    return redirect(f"{request.META.get('HTTP_REFERER')}#proposed_answers")
