from django.shortcuts import render
from django.db.models import Count, Q
from drevo.models.interview_answer_expert_proposal import InterviewAnswerExpertProposal

def dimensional_distributions_1(request):
    questions = []
    all_answers = {}
    total_voters = 0
    all_participants = 0

    selected_interview = request.GET.get('selected_interview') 
    questions = list(set(InterviewAnswerExpertProposal.objects.filter(
        question__is_published=True, 
        interview__name=selected_interview
    ).order_by('question__order').values_list('question__name', flat=True).distinct()))
    selected_question = request.GET.get('selected_question')

    answers = InterviewAnswerExpertProposal.objects.filter(
        answer__is_published=True,
        question__name=selected_question,
        is_agreed=True
    ).order_by('answer__order').values('answer__name').annotate(
        agreed_count=Count('expert', filter=Q(is_agreed=True))
    )

    total_voters = answers.values('expert').distinct().count()
    all_participants = InterviewAnswerExpertProposal.objects.filter(
        question__is_published=True, 
        interview__name=selected_interview,
        is_agreed=True
    ).values('expert').distinct().count()

    for answer in answers:
        answer_id = answer['answer__name']
        agreed_count = answer['agreed_count']
        if answer_id not in all_answers:
            all_answers[answer_id] = agreed_count
        else:
            all_answers[answer_id] += agreed_count

    table = [{'answer_name': answer_id, 
              'agreed_count': agreed_count, 
              'percent': (agreed_count / answers.count()) * 100} for answer_id, agreed_count in all_answers.items()]
    context = {
        'selected_interview': selected_interview, 
        'questions': questions, 
        'selected_question': selected_question,
        'table': table, 
        'total_voters': total_voters, 
        'all_participants': all_participants
    }
    return render(request, 'drevo/dimensional_distributions_1.html', context)