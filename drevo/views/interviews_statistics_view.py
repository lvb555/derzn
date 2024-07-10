from django.shortcuts import render
from django.db.models import Count, Q
from collections import Counter
from collections import Counter
from collections import defaultdict
from drevo.models.interview_answer_expert_proposal import InterviewAnswerExpertProposal
from django.shortcuts import render, get_object_or_404
from drevo.models.knowledge import Znanie

def dimensional_distributions_1(request, id):
    total_voters = 0
    all_participants = 0

    selected_interview = get_object_or_404(Znanie, id=id)
    questions = list(InterviewAnswerExpertProposal.objects.filter(
    questions = list(InterviewAnswerExpertProposal.objects.filter(
        question__is_published=True, 
        interview=selected_interview,
        is_agreed=True,
        answer__isnull=False
    ).order_by('question__order').values('question__id', 'question__name').distinct())
    ).order_by('question__order').values('question__id', 'question__name').distinct())
    selected_question_id = request.GET.get('selected_question_id')
    if selected_question_id:
        selected_question = get_object_or_404(Znanie, id=selected_question_id)
    else:
        if questions:
            obj = questions[0]
            selected_question = get_object_or_404(Znanie, id=obj['question__id'])  
        else: 
            selected_question = None
        if questions:
            obj = questions[0]
            selected_question = get_object_or_404(Znanie, id=obj['question__id'])  
        else: 
            selected_question = None
    answers = InterviewAnswerExpertProposal.objects.filter(
        answer__is_published=True,
        interview=selected_interview,
        question=selected_question,
        is_agreed=True,
        answer__isnull=False
    ).order_by('answer__order').values('answer__name').annotate(
        agreed_count=Count('expert', filter=Q(is_agreed=True))
    ).distinct()


    total_voters = InterviewAnswerExpertProposal.objects.filter(
        interview=selected_interview,
        question=selected_question,
        is_agreed=True,
        answer__isnull=False  
    ).values('expert').distinct().count()


    all_participants = InterviewAnswerExpertProposal.objects.filter( 
        interview=selected_interview,
        is_agreed=True,
        answer__isnull=False  
    ).values('expert').distinct().count()

    table = []
    table = []
    for answer in answers:
        answer_id = answer['answer__name']
        agreed_count = answer['agreed_count']
        percent = (agreed_count / total_voters) * 100
        table.append({
            'answer_name': answer_id,
            'agreed_count': agreed_count,
            'percent': percent,
        })
    
        percent = (agreed_count / total_voters) * 100
        table.append({
            'answer_name': answer_id,
            'agreed_count': agreed_count,
            'percent': percent,
        })
    
    context = {
        'selected_interview': selected_interview, 
        'questions': questions,  # Используйте обновленный список вопросов
        'questions': questions,  # Используйте обновленный список вопросов
        'selected_question': selected_question,
        'table': table, 
        'total_voters': total_voters, 
        'all_participants': all_participants
    }
    return render(request, 'drevo/dimensional_distributions_1.html', context)

def dimensional_distributions_2(request, id):
    selected_interview = get_object_or_404(Znanie, id=id)

    selected_question_1_id = request.GET.get('selected_question_1_id')
    selected_question_1 = get_object_or_404(Znanie, id=selected_question_1_id) if selected_question_1_id else None

    selected_question_2_id = request.GET.get('selected_question_2_id')
    selected_question_2 = get_object_or_404(Znanie, id=selected_question_2_id) if selected_question_2_id else None

    questions = list(InterviewAnswerExpertProposal.objects.filter(
        question__is_published=True, 
        interview=selected_interview,
        is_agreed=True,
        answer__isnull=False
    ).order_by('question__order').values('question__id', 'question__name').distinct())

    experts_agreed_1 = InterviewAnswerExpertProposal.objects.filter(
        Q(question=selected_question_1),
        interview=selected_interview,
        is_agreed=True,
        answer__isnull=False 
    ).values('answer__name', 'expert__id').distinct()

    experts_agreed_2 = InterviewAnswerExpertProposal.objects.filter(
        Q(question=selected_question_2),
        interview=selected_interview,
        is_agreed=True,
        answer__isnull=False 
    ).values('answer__name', 'expert__id').order_by('answer__order').distinct()

    answers_1 = InterviewAnswerExpertProposal.objects.filter(
        interview=selected_interview,
        question=selected_question_1,
        is_agreed=True,
        answer__isnull=False 
    ).values_list('answer__name', flat=True).order_by('answer__order').distinct()

    answers_2 = InterviewAnswerExpertProposal.objects.filter(
        interview=selected_interview,
        question=selected_question_2,
        is_agreed=True,
        answer__isnull=False 
    ).values_list('answer__name', flat=True).order_by('answer__order').distinct()
    all_participants = InterviewAnswerExpertProposal.objects.filter( 
        interview=selected_interview,
        is_agreed=True,
        answer__isnull=False  
    ).values('expert').distinct().count()

    total_counts = Counter(expert_2['answer__name'] 
        for expert_2 in experts_agreed_2 
            if any(expert_2['expert__id'] == expert_1['expert__id'] 
                for expert_1 in experts_agreed_1))

    total_counts = Counter(expert_2['answer__name'] 
        for expert_2 in experts_agreed_2 
            if any(expert_2['expert__id'] == expert_1['expert__id'] 
                for expert_1 in experts_agreed_1))

    common_experts = defaultdict(lambda: defaultdict(lambda: {'count': 0, 'percentage': 0, 'total': 0}))
    for expert_1 in experts_agreed_1:
        answer_1 = expert_1['answer__name']
        for expert_2 in experts_agreed_2:
            answer_2 = expert_2['answer__name']  
            answer_2 = expert_2['answer__name']  
            if expert_1['expert__id'] == expert_2['expert__id']:
                common_experts[answer_1][answer_2]['count'] += 1
                if total_counts[answer_2] > 0:
                    # Вычисляем процент согласных экспертов
                    common_experts[answer_1][answer_2]['percentage'] = (common_experts[answer_1][answer_2]['count'] / total_counts[answer_2]) * 100
                else:
                    common_experts[answer_1][answer_2]['percentage'] = 0
    table = []
    for answer1 in answers_1:
        row = {'answer1': answer1, 'cells': [], 'totals': []}
        for answer2 in answers_2:
            data = common_experts[answer1].get(answer2, {'count': 0, 'percentage': 0})
            row['cells'].append(data)
        for total in total_counts.values():
            row['totals'].append(total)
        table.append(row)

    context = {
        'table': table,
        'questions': questions,
        'questions': questions,
        'selected_question_1': selected_question_1,
        'selected_question_2': selected_question_2,
        'selected_interview': selected_interview,
        'answers_2': answers_2,
        'all_participants': all_participants
    }
    return render(request, 'drevo/dimensional_distributions_2.html', context) 