from django.shortcuts import render
from loguru import logger
from users.models import User, MenuSections
from ..models import Znanie, CategoryExpert, InterviewAnswerExpertProposal
from ..relations_tree import get_knowledges_by_categories
from drevo.common import variables


logger.add('logs/main.log',
           format="{time} {level} {message}", rotation='100Kb', level="ERROR")


def my_interview(request, id):
    if request.method == 'GET':
        proposal_results = {}
        user = User.objects.filter(id=id).first()
        context = {}
        if user is not None:
            if user == request.user:
                context['sections'] = [i.name for i in MenuSections.objects.all()]
                context['activity'] = [i.name for i in MenuSections.objects.all() if i.name.startswith('Мои') or
                                       i.name.startswith('Моя')]
                context['link'] = 'users:myprofile'
            else:
                context['sections'] = [i.name for i in user.sections.all()]
                context['activity'] = [i.name for i in user.sections.all() if
                                       i.name.startswith('Мои') or i.name.startswith('Моя')]
                context['link'] = 'public_human'
                context['id'] = id
            context['pub_user'] = user
            all_proposals = InterviewAnswerExpertProposal.objects.filter(expert=user, new_answer_text='')
            all_interviews_name = all_proposals.values_list("interview__name", flat=True).distinct()
            for interview in all_interviews_name:
                questions_and_answers = {}
                all_questions_name = all_proposals.filter(interview__name=interview).values_list("question__name", flat=True) \
                    .distinct().order_by('-question__order')
                for questions in all_questions_name:
                    questions_and_answers[questions] = all_proposals.filter(question__name=questions, interview__name=interview) \
                        .values_list("answer__name", "is_agreed").order_by('-answer__order')
                proposal_results[interview] = questions_and_answers
                context['proposal_results'] = proposal_results
            context['title'] = 'Мои ответы'
            return render(request, 'drevo/interview_and_proposal.html', context)

def my_proposal(request, id):
    if request.method == 'GET':
        proposal_results = {}
        user = User.objects.filter(id=id).first()
        context = {}
        if user is not None:
            if user == request.user:
                context['sections'] = [i.name for i in MenuSections.objects.all()]
                context['activity'] = [i.name for i in MenuSections.objects.all() if i.name.startswith('Мои') or
                                       i.name.startswith('Моя')]
                context['link'] = 'users:myprofile'
            else:
                context['sections'] = [i.name for i in user.sections.all()]
                context['activity'] = [i.name for i in user.sections.all() if
                                       i.name.startswith('Мои') or i.name.startswith('Моя')]
                context['link'] = 'public_human'
                context['id'] = id
            context['pub_user'] = user
            all_proposals = InterviewAnswerExpertProposal.objects.filter(expert=user).exclude(new_answer_text='')
            all_interviews_name = all_proposals.values_list("interview__name", flat=True).distinct()
            for interview in all_interviews_name:
                questions_and_answers = {}
                all_questions_name = all_proposals.filter(interview__name=interview).values_list("question__name", flat=True) \
                    .distinct().order_by('-question__order')
                for questions in all_questions_name:
                    questions_and_answers[questions] = all_proposals.filter(question__name=questions, interview__name=interview) \
                        .values_list("new_answer_text", "status").order_by('-answer__order')
                proposal_results[interview] = questions_and_answers
                context['proposal_results'] = proposal_results
            context['title'] = 'Мои предложения'
            return render(request, 'drevo/interview_and_proposal.html', context)
