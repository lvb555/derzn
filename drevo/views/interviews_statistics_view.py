from django.shortcuts import render
from django.db.models import Count, Q
from collections import defaultdict
from drevo.models.interview_answer_expert_proposal import InterviewAnswerExpertProposal
from django.shortcuts import render, get_object_or_404
from drevo.models.knowledge import Znanie

def dimensional_distributions_1(request, id):
    question_list = []
    all_answers = {}
    total_voters = 0
    all_participants = 0

    selected_interview = get_object_or_404(Znanie, id=id)
    questions = InterviewAnswerExpertProposal.objects.filter(
        question__is_published=True, 
        interview=selected_interview,
        is_agreed=True,
        answer__isnull=False
    ).order_by('question__order').distinct()
    for question in questions:
        if question.answer is not None:
            if question.question not in question_list:
                question_list.append(question.question)
    selected_question_id = request.GET.get('selected_question_id')
    if selected_question_id:
        selected_question = get_object_or_404(Znanie, id=selected_question_id)
    else:
        selected_question = question_list[0]
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

    for answer in answers:
        answer_id = answer['answer__name']
        agreed_count = answer['agreed_count']
        all_answers[answer_id] = agreed_count
        
    table = [{'answer_name': answer_id, 
        'agreed_count': agreed_count, 
        'percent': (agreed_count / total_voters) * 100} for answer_id, agreed_count in all_answers.items()]
        
    context = {
        'selected_interview': selected_interview, 
        'questions': question_list, 
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

    question_list = []
    questions = InterviewAnswerExpertProposal.objects.filter(
        question__is_published=True, 
        interview=selected_interview,
        is_agreed=True,
        answer__isnull=False 
    ).order_by('question__order')
    for question in questions:
        if question.question not in question_list:
            question_list.append(question.question)

    experts_agreed_1 = InterviewAnswerExpertProposal.objects.filter(
        Q(question=selected_question_1),
        interview=selected_interview,
        is_agreed=True,
        answer__isnull=False 
    ).values('answer__name', 'expert__id').order_by('answer__order').distinct()

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

    common_experts = defaultdict(lambda: defaultdict(lambda: {'count': 0, 'percentage': 0, 'total': 0}))
    common_expert_ids = set(expert['expert__id'] for expert in experts_agreed_1
    ).intersection(expert['expert__id'] for expert in experts_agreed_2)

    # Подсчитайте количество общих экспертов
    total_common_experts = len(common_expert_ids)

    # Теперь переберем экспертов и вычислим common_experts
    for expert_1 in experts_agreed_1:
        answer_1 = expert_1['answer__name']
        for expert_2 in experts_agreed_2:
            answer_2 = expert_2['answer__name']
            if expert_1['expert__id'] == expert_2['expert__id']:
                # Увеличиваем счетчик согласованных экспертов для данной пары ответов
                common_experts[answer_1][answer_2]['count'] += 1
                # Заполняем общее количество для answer_2
                common_experts[answer_1][answer_2]['total'] = total_common_experts
                if common_experts[answer_1][answer_2]['total'] > 0:
                    # Вычисляем процент согласованных экспертов
                    common_experts[answer_1][answer_2]['percentage'] = (common_experts[answer_1][answer_2]['count'] / common_experts[answer_1][answer_2]['total']) * 100
                else:
                    common_experts[answer_1][answer_2]['percentage'] = 0
    table = []
    for answer1 in answers_1:
        row = {'answer1': answer1, 'cells': [], 'totals': []}
        for answer2 in answers_2:
            data = common_experts[answer1].get(answer2, {'count': 0, 'percentage': 0})
            row['cells'].append(data)
            # Извлекаем соответствующее общее количество для этого ответа
            total_count_for_answer2 = common_experts[answer1][answer2]['total']
            row['totals'].append(total_count_for_answer2)
        table.append(row)

    context = {
        'table': table,
        'questions': question_list,
        'selected_question_1': selected_question_1,
        'selected_question_2': selected_question_2,
        'selected_interview': selected_interview,
        'answers_2': answers_2,
        'all_participants': all_participants
    }
    return render(request, 'drevo/dimensional_distributions_2.html', context) 