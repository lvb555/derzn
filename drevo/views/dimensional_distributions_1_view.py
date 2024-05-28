from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Count, Q
from drevo.models.interview_answer_expert_proposal import InterviewAnswerExpertProposal
from drevo.views.interviews_all_view import get_interviews_all
from django.db.models import Prefetch


def dimensional_distributions_1(request):
    # Загружаем связанные объекты, чтобы избежать дополнительных запросов
    category_interviews = get_interviews_all()
    category_interview_names = [interview.name for category, interviews in category_interviews for interview in interviews]
    interviews = list(set(InterviewAnswerExpertProposal.objects.filter(
        interview__is_published=True, 
        interview__name__in=category_interview_names
    ).values_list('interview__name', flat=True)))

    questions = []
    all_answers = {}
    total_voters = 0

    if 'selected_interview' in request.GET:
        selected_interview = request.GET['selected_interview']
        questions = list(set(InterviewAnswerExpertProposal.objects.filter(question__is_published=True, interview__name=selected_interview).values_list('question__name', flat=True)))

    if 'selected_question' in request.GET:
        selected_question = request.GET['selected_question']
        answers = InterviewAnswerExpertProposal.objects.filter(
            answer__is_published=True,
            question__name=selected_question
        ).values('answer__name').annotate(
            agreed_count=Count('expert', filter=Q(is_agreed=True))
        )

        for answer in answers:
            answer_id = answer['answer__name']
            agreed_count = answer['agreed_count']
            if answer_id not in all_answers:
                all_answers[answer_id] = agreed_count
            else:
                all_answers[answer_id] += agreed_count
            total_voters += agreed_count

    table = [{'answer_name': answer_id, 
            'agreed_count': agreed_count, 
            'percent': (agreed_count / total_voters) * 100} for answer_id, agreed_count in all_answers.items()]

    if request.is_ajax():
        if 'interview' in request.GET:
            return JsonResponse({'questions': questions})
        elif 'question' in request.GET:
            return JsonResponse({'table': table})

    return render(request, 'drevo/dimensional_distributions_1.html', {'interviews': interviews, 'questions': questions, 
    'table': table, 'total_voters': total_voters
    })
