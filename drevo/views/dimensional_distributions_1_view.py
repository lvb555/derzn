from django.shortcuts import render
from django.db.models import Count, Q
from drevo.models.interview_answer_expert_proposal import InterviewAnswerExpertProposal

def dimensional_distributions_1(request):
    questions = []
    all_answers = {}
    total_voters = 0
    all_participants = 0
    selected_interview = request.GET.get('selected_interview')  # Используем get() для безопасного доступа к параметру
    questions = list(set(InterviewAnswerExpertProposal.objects.filter(question__is_published=True, interview__name=selected_interview).order_by('question__order').values_list('question__name', flat=True)))
    selected_question = request.GET.get('selected_question')
    if selected_question:
        interview_object = InterviewAnswerExpertProposal.objects.filter(question__name=selected_question).first()
        if interview_object:
            selected_interview = interview_object.interview.name
    
        questions = list(set(InterviewAnswerExpertProposal.objects.filter(question__is_published=True, interview__name=selected_interview).order_by('question__order').values_list('question__name', flat=True)))
        answers = InterviewAnswerExpertProposal.objects.filter(
            answer__is_published=True,
            question__name=selected_question
        ).values('answer__name').order_by('answer__order').annotate(
            agreed_count=Count('expert', filter=Q(is_agreed=True))
        )
        total_voters = answers.values('expert').distinct().count()
        all_participants = InterviewAnswerExpertProposal.objects.filter(
            question__is_published=True, 
            interview__name=selected_interview
        ).values('expert').distinct().count()
        for answer in answers:
            answer_id = answer['answer__name']
            agreed_count = answer['agreed_count']
            if answer_id not in all_answers:
                all_answers[answer_id] = agreed_count
            else:
                all_answers[answer_id] += agreed_count
    if selected_interview == None:
        selected_interview = selected_interview
    table = [{'answer_name': answer_id, 
              'agreed_count': agreed_count, 
              'percent': (agreed_count / answers.count()) * 100} for answer_id, agreed_count in all_answers.items()]

    return render(request, 'drevo/dimensional_distributions_1.html', {
        'selected_interview': selected_interview, 'questions': questions, 
        'table': table, 'total_voters': total_voters, 'all_participants': all_participants, 
    })
