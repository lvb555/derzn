from django.shortcuts import render
from django.db.models import Count, Q
from drevo.models.interview_answer_expert_proposal import InterviewAnswerExpertProposal
from drevo.views.interviews_all_view import get_interviews_all

def dimensional_distributions_1(request):
    category_interviews = get_interviews_all()
    category_interview_names = [interview.name for category, interviews in category_interviews for interview in interviews]
    interviews = list(set(InterviewAnswerExpertProposal.objects.filter(
        interview__is_published=True, 
        interview__name__in=category_interview_names
    ).values_list('interview__name', flat=True)))

    questions = []
    all_answers = {}
    total_voters = 0
    all_participants = 0

    selected_interview = request.GET.get('selected_interview')  # Используем get() для безопасного доступа к параметру
    questions = list(set(InterviewAnswerExpertProposal.objects.filter(question__is_published=True, interview__name=selected_interview).values_list('question__name', flat=True)))
    selected_question = request.GET.get('selected_question')
    if selected_question:
        interview_object = InterviewAnswerExpertProposal.objects.filter(question__name=selected_question).first()
        if interview_object:
            selected_interview_ = interview_object.interview.name
        questions = list(set(InterviewAnswerExpertProposal.objects.filter(question__is_published=True, interview__name=selected_interview_).values_list('question__name', flat=True)))
        answers = InterviewAnswerExpertProposal.objects.filter(
            answer__is_published=True,
            question__name=selected_question
        ).values('answer__name').annotate(
            agreed_count=Count('expert', filter=Q(is_agreed=True))
        )
        total_voters = answers.values('expert').distinct().count()
        all_participants = InterviewAnswerExpertProposal.objects.filter(
            question__is_published=True, 
            interview__name=selected_interview_
        ).values('expert').distinct().count()
        for answer in answers:
            answer_id = answer['answer__name']
            agreed_count = answer['agreed_count']
            if answer_id not in all_answers:
                all_answers[answer_id] = agreed_count
                print(all_answers)
            else:
                all_answers[answer_id] += agreed_count
                print(all_answers)

    table = [{'answer_name': answer_id, 
              'agreed_count': agreed_count, 
              'percent': (agreed_count / answers.count()) * 100} for answer_id, agreed_count in all_answers.items()]

    if selected_interview == None:
        selected_interview = selected_interview_

    return render(request, 'drevo/dimensional_distributions_1.html', {
        'interviews': interviews, 'questions': questions, 
        'table': table, 'total_voters': total_voters, 'all_participants': all_participants, 'selected_interview': selected_interview
    })