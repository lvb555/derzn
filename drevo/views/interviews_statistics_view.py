from django.shortcuts import render
from django.db.models import Count, Q
from collections import defaultdict
from drevo.models.interview_answer_expert_proposal import InterviewAnswerExpertProposal
from django.shortcuts import render, get_object_or_404
from drevo.models.knowledge import Znanie

def dimensional_distributions_1(request, id):
    questions = []
    all_answers = {}
    total_voters = 0
    all_participants = 0

    selected_interview = get_object_or_404(Znanie, id=id)
    questions = list(set(InterviewAnswerExpertProposal.objects.filter(
        question__is_published=True, 
        interview=selected_interview
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
          'percent': (agreed_count / total_voters) * 100} for answer_id, agreed_count in all_answers.items()]

    context = {
        'selected_interview': selected_interview, 
        'questions': questions, 
        'selected_question': selected_question,
        'table': table, 
        'total_voters': total_voters, 
        'all_participants': all_participants
    }
    return render(request, 'drevo/dimensional_distributions_1.html', context)

def dimensional_distributions_2(request, id):
    selected_interview = get_object_or_404(Znanie, id=id)
    selected_question_1 = request.GET.get('selected_question_1')
    selected_question_2 = request.GET.get('selected_question_2')

    questions = list(set(InterviewAnswerExpertProposal.objects.filter(
        question__is_published=True,
        interview=selected_interview
    ).order_by('question__order').values_list('question__name', flat=True)))

    experts_agreed_1 = InterviewAnswerExpertProposal.objects.filter(
        Q(question__name=selected_question_1),
        interview__name=selected_interview,
        is_agreed=True
    ).values('answer__name', 'expert__id').order_by('answer__order')

    experts_agreed_2 = InterviewAnswerExpertProposal.objects.filter(
        Q(question__name=selected_question_2),
        interview__name=selected_interview,
        is_agreed=True
    ).values('answer__name', 'expert__id').order_by('answer__order')

    answers_1 = list(set(InterviewAnswerExpertProposal.objects.filter(
        question__name=selected_question_1
    ).order_by('answer__order').values_list('answer__name', flat=True)))

    answers_2 = list(set(InterviewAnswerExpertProposal.objects.filter(
        question__name=selected_question_2
    ).order_by('answer__order').values_list('answer__name', flat=True)))

    total_counts = {}
    for answer2 in answers_2:
        total_counts[answer2] = InterviewAnswerExpertProposal.objects.filter(
            Q(answer__name=answer2),
            is_agreed=True
        ).values('expert__id').distinct().count()
        
    common_experts = defaultdict(lambda: defaultdict(lambda: {'count': 0, 'percentage': 0, 'total': 0}))
    for expert_1 in experts_agreed_1:
        answer_1 = expert_1['answer__name']
        for expert_2 in experts_agreed_2:
            answer_2 = expert_2['answer__name']  
            if expert_1['expert__id'] == expert_2['expert__id']:
                common_experts[answer_1][answer_2]['count'] += 1
                common_experts[answer_1][answer_2]['total'] = total_counts[answer2]
                common_experts[answer_1][answer_2]['percentage'] = (common_experts[answer_1][answer_2]['count'] / total_counts[answer2]) * 100 if total_counts[answer2] > 0 else 0
    table = []
    for answer1 in answers_1:
        row = {'answer1': answer1, 'cells': [], 'totals': []}
        for answer2 in answers_2:
            data = common_experts[answer1].get(answer2, {'count': 0, 'percentage': 0})
            row['cells'].append(data)
            row['totals'].append(total_counts[answer2])
        table.append(row)
    for row in table:
        for i, cell in enumerate(row['cells']):
            cell['percentage'] = (cell['count'] / row['totals'][i]) * 100 if row['totals'][i] > 0 else 0
    context = {
        'table': table,
        'questions': questions,
        'selected_question_1': selected_question_1,
        'selected_question_2': selected_question_2,
        'selected_interview': selected_interview,
        'answers_2': answers_2
    }
    return render(request, 'drevo/dimensional_distributions_2.html', context) 