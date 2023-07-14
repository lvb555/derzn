from django.db.models import Q
from django.shortcuts import render
from loguru import logger
from users.models import User, MenuSections
from users.views import access_sections
from ..models import Znanie, SpecialPermissions, InterviewAnswerExpertProposal, FriendsInviteTerm, Message
from ..models.feed_messages import FeedMessage
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
                context['sections'] = access_sections(user)
                context['activity'] = [i for i in context['sections'] if i.startswith('Мои') or
                                       i.startswith('Моя')]
                context['link'] = 'users:myprofile'
                invite_count = len(FriendsInviteTerm.objects.filter(recipient=user.id))
                context['invite_count'] = invite_count if invite_count else 0
                context['new_knowledge_feed'] = FeedMessage.objects.filter(recipient=user, was_read=False).count()
                context['new_messages'] = Message.objects.filter(recipient=user, was_read=False).count()
                context['new'] = int(context['new_knowledge_feed']) + int(
                    context['invite_count'] + int(context['new_messages']))
            else:
                context['sections'] = [i.name for i in user.sections.all()]
                context['activity'] = [i.name for i in user.sections.all() if
                                       i.name.startswith('Мои') or i.name.startswith('Моя')]
                context['link'] = 'public_human'
                context['id'] = id
            context['pub_user'] = user
            all_proposals = InterviewAnswerExpertProposal.objects.filter(Q(new_answer_text=None) | Q(new_answer_text=''))
            all_proposals = all_proposals.filter(expert=user, is_agreed=True)
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
                context['sections'] = access_sections(user)
                context['activity'] = [i for i in context['sections'] if i.startswith('Мои') or
                                       i.startswith('Моя')]
                context['link'] = 'users:myprofile'
                invite_count = len(FriendsInviteTerm.objects.filter(recipient=user.id))
                context['invite_count'] = invite_count if invite_count else 0
                context['new_knowledge_feed'] = FeedMessage.objects.filter(recipient=user, was_read=False).count()
                context['new_messages'] = Message.objects.filter(recipient=user, was_read=False).count()
                context['new'] = int(context['new_knowledge_feed']) + int(
                    context['invite_count'] + int(context['new_messages']))
            else:
                context['sections'] = [i.name for i in user.sections.all()]
                context['activity'] = [i.name for i in user.sections.all() if
                                       i.name.startswith('Мои') or i.name.startswith('Моя')]
                context['link'] = 'public_human'
                context['id'] = id
            context['pub_user'] = user
            all_proposals = InterviewAnswerExpertProposal.objects.filter(expert=user).exclude(Q(new_answer_text=None) | Q(new_answer_text=''))
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
