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
# # views.py
# from django.shortcuts import render
# from django.http import JsonResponse
# from django.db.models import Count, Q
# from drevo.models.interview_answer_expert_proposal import InterviewAnswerExpertProposal
# from drevo.views.interviews_all_view import get_interviews_all

# def dimensional_distributions_1(request):
#     category_interviews = get_interviews_all()
#     category_interview_names = [interview.name for category, interviews in category_interviews for interview in interviews]
#     interviews = list(set(InterviewAnswerExpertProposal.objects.filter(interview__is_published=True, interview__name__in=category_interview_names).values_list('interview__name', flat=True)))
#     questions = []
#     answers = []
#     all_answers = {}  # Создаем словарь для хранения суммарных значений agreed_count
#     total_voters = 0  # Общее количество проголосовавших

#     if 'selected_interview' in request.GET:
#         selected_interview = request.GET['selected_interview']
#         questions = list(set(InterviewAnswerExpertProposal.objects.filter(question__is_published=True, interview__name=selected_interview).values_list('question__name', flat=True)))

#     if 'selected_question' in request.GET:
#         selected_question = request.GET['selected_question']
#         answers = InterviewAnswerExpertProposal.objects.filter(
#             answer__is_published=True,
#             question__name=selected_question
#         ).values('answer__name').annotate(
#             agreed_count=Count('expert', filter=Q(is_agreed=True))
#         )

#         # Суммируем agreed_count для одинаковых ID ответов
#         for answer in answers:
#             answer_id = answer['answer__name']
#             agreed_count = answer['agreed_count']
#             if answer_id not in all_answers:
#                 all_answers[answer_id] = agreed_count
#                 total_voters += agreed_count
#             else:
#                 all_answers[answer_id] += agreed_count
#                 total_voters += agreed_count

#     # Вычисляем проценты для каждого ответа
#     for answer_id, agreed_count in all_answers.items():
#         percent = (agreed_count / total_voters) * 100
#         all_answers[answer_id] = (agreed_count, percent)

#     if request.is_ajax():
#         if 'interview' in request.GET:
#             return JsonResponse({'questions': questions})
#         elif 'question' in request.GET:
#             # Создаем список словарей с данными answer_name, agreed_count и percent
#             table = [{'answer_name': answer_id, 'agreed_count': agreed_count, 'percent': percent} for answer_id, (agreed_count, percent) in all_answers.items()]
#             return JsonResponse({'table': table})

#     return render(request, 'drevo/dimensional_distributions_1.html', {'interviews': interviews, 'questions': questions, 'answers': answers, 'all_answers': all_answers, 'total_voters': total_voters})

# from django.shortcuts import render
# from django.http import JsonResponse
# from django.db.models import Count, Q
# from drevo.models.interview_answer_expert_proposal import InterviewAnswerExpertProposal
# from drevo.views.interviews_all_view import get_interviews_all

# def dimensional_distributions_1(request):
#     category_interviews = get_interviews_all()
#     category_interview_names = [interview.name for category, interviews in category_interviews for interview in interviews]
#     interviews = list(set(InterviewAnswerExpertProposal.objects.filter(interview__is_published=True, interview__name__in=category_interview_names).values_list('interview__name', flat=True)))
#     questions = []
#     answers = []
#     all_answers = {}  # Create a dictionary to store aggregated agreed_count values
#     total_voters = 0  # Total number of voters

#     if 'selected_interview' in request.GET:
#         selected_interview = request.GET['selected_interview']
#         questions = list(set(InterviewAnswerExpertProposal.objects.filter(question__is_published=True, interview__name=selected_interview).values_list('question__name', flat=True)))

#     if 'selected_question' in request.GET:
#         selected_question = request.GET['selected_question']
#         answers = InterviewAnswerExpertProposal.objects.filter(
#             answer__is_published=True,
#             question__name=selected_question
#         ).values('answer__name').annotate(
#             agreed_count=Count('expert', filter=Q(is_agreed=True))
#         )

#         # Sum agreed_count for identical answer IDs
#         for answer in answers:
#             answer_id = answer['answer__name']
#             agreed_count = answer['agreed_count']
#             if answer_id not in all_answers:
#                 all_answers[answer_id] = agreed_count
#                 total_voters += agreed_count
#             else:
#                 all_answers[answer_id] += agreed_count
#                 total_voters += agreed_count

#     # Calculate percentages for each answer
#     for answer_id, agreed_count in all_answers.items():
#         percent = (agreed_count / total_voters) * 100
#         all_answers[answer_id] = (agreed_count, percent)

#     if request.is_ajax():
#         if 'interview' in request.GET:
#             return JsonResponse({'questions': questions})
#         elif 'question' in request.GET:
#             # Create a list of dictionaries containing answer_name, agreed_count, and percent
#             table = [{'answer_name': answer_id, 'agreed_count': agreed_count, 'percent': percent} for answer_id, (agreed_count, percent) in all_answers.items()]
#             return JsonResponse({'table': table})

#     return render(request, 'drevo/dimensional_distributions_1.html', {'interviews': interviews, 'questions': questions, 'answers': answers, 'all_answers': all_answers, 'total_voters': total_voters})


# views.py
# from django.shortcuts import render
# from django.http import JsonResponse
# from django.db.models import Count, Q
# from drevo.models.interview_answer_expert_proposal import InterviewAnswerExpertProposal
# from drevo.views.interviews_all_view import get_interviews_all

# def dimensional_distributions_1(request):
#     category_interviews = get_interviews_all()
#     category_interview_names = [interview.name for category, interviews in category_interviews for interview in interviews]
#     interviews = list(set(InterviewAnswerExpertProposal.objects.filter(interview__is_published=True, interview__name__in=category_interview_names).values_list('interview__name', flat=True)))
#     questions = []
#     answers = []
#     all_answers = {}  # Создаем словарь для хранения суммарных значений agreed_count
#     total_voters = 0  # Общее количество проголосовавших

#     if 'selected_interview' in request.GET:
#         selected_interview = request.GET['selected_interview']
#         questions = list(set(InterviewAnswerExpertProposal.objects.filter(question__is_published=True, interview__name=selected_interview).values_list('question__name', flat=True)))

#     if 'selected_question' in request.GET:
#         selected_question = request.GET['selected_question']
#         answers = InterviewAnswerExpertProposal.objects.filter(
#             answer__is_published=True,
#             question__name=selected_question
#         ).values('answer__name').annotate(
#             agreed_count=Count('expert', filter=Q(is_agreed=True))
#         )

#         # Суммируем agreed_count для одинаковых ID ответов
#         for answer in answers:
#             answer_id = answer['answer__name']
#             agreed_count = answer['agreed_count']
#             if answer_id not in all_answers:
#                 all_answers[answer_id] = agreed_count
#                 total_voters += agreed_count
#             else:
#                 all_answers[answer_id] += agreed_count
#                 total_voters += agreed_count

#     # Вычисляем проценты для каждого ответа
#     for answer_id, agreed_count in all_answers.items():
#         percent = (agreed_count / total_voters) * 100
#         all_answers[answer_id] = (agreed_count, percent)

#     if request.is_ajax():
#         if 'interview' in request.GET:
#             return JsonResponse({'questions': questions})
#         elif 'question' in request.GET:
#             return JsonResponse({'answers': list(answers)})

#     return render(request, 'drevo/dimensional_distributions_1.html', {'interviews': interviews, 'questions': questions, 'answers': answers, 'all_answers': all_answers, 'total_voters': total_voters})

# views.py
# from django.shortcuts import render
# from django.http import JsonResponse
# from django.db.models import Count, Q
# from drevo.models.interview_answer_expert_proposal import InterviewAnswerExpertProposal
# from drevo.views.interviews_all_view import get_interviews_all

# def dimensional_distributions_1(request):
#     category_interviews = get_interviews_all()
#     category_interview_names = [interview.name for category, interviews in category_interviews for interview in interviews]
#     interviews = list(set(InterviewAnswerExpertProposal.objects.filter(interview__is_published=True, interview__name__in=category_interview_names).values_list('interview__name', flat=True)))
#     questions = []
#     answers = []
#     all_answers = {}  # Создаем словарь для хранения суммарных значений agreed_count
#     total_voters = 0  # Общее количество проголосовавших
#     percent = 0

#     if 'selected_interview' in request.GET:
#         selected_interview = request.GET['selected_interview']
#         questions = list(set(InterviewAnswerExpertProposal.objects.filter(question__is_published=True, interview__name=selected_interview).values_list('question__name', flat=True)))

#     if 'selected_question' in request.GET:
#         selected_question = request.GET['selected_question']
#         answers = InterviewAnswerExpertProposal.objects.filter(
#             answer__is_published=True,
#             question__name=selected_question
#         ).values('answer__name').annotate(
#             agreed_count=Count('expert', filter=Q(is_agreed=True))
#         )

#         # Суммируем agreed_count для одинаковых ID ответов
#         for answer in answers:
    
#             answer_id = answer['answer__name']
#             agreed_count = answer['agreed_count']
#             if answer_id not in all_answers:
#                 all_answers[answer_id] = agreed_count
#                 total_voters += agreed_count
#                 percent = all_answers[answer_id] / total_voters * 100 
#             else:
#                 all_answers[answer_id] += agreed_count
#                 total_voters += agreed_count
#                 percent = all_answers[answer_id] / total_voters * 100 
            
#     if request.is_ajax():
#         if 'interview' in request.GET:
#             return JsonResponse({'questions': questions})
#         elif 'question' in request.GET:
#             return JsonResponse({'answers': list(answers)})

#     return render(request, 'drevo/dimensional_distributions_1.html', {'interviews': interviews, 'questions': questions, 'answers': answers, 'all_answers': all_answers, 'total_voters': total_voters, 'percent': percent})


# views.py
# from django.shortcuts import render
# from django.http import JsonResponse
# from django.db.models import Count, Q
# from drevo.models.interview_answer_expert_proposal import InterviewAnswerExpertProposal
# from drevo.views.interviews_all_view import get_interviews_all

# def dimensional_distributions_1(request):
#     category_interviews = get_interviews_all()
#     category_interview_names = [interview.name for category, interviews in category_interviews for interview in interviews]
#     interviews = list(set(InterviewAnswerExpertProposal.objects.filter(interview__is_published=True, interview__name__in=category_interview_names).values_list('interview__name', flat=True)))
#     questions = []
#     answers = []
#     all_answers = {}  # Создаем словарь для хранения суммарных значений agreed_count

#     if 'selected_interview' in request.GET:
#         selected_interview = request.GET['selected_interview']
#         questions = list(set(InterviewAnswerExpertProposal.objects.filter(question__is_published=True, interview__name=selected_interview).values_list('question__name', flat=True)))

#     if 'selected_question' in request.GET:
#         selected_question = request.GET['selected_question']
#         answers = InterviewAnswerExpertProposal.objects.filter(
#             answer__is_published=True,
#             question__name=selected_question
#         ).values('answer__name').annotate(
#             agreed_count=Count('expert', filter=Q(is_agreed=True))
#         )

#         # Суммируем agreed_count для одинаковых ID ответов
#         for answer in answers:
#             answer_id = answer['answer__name']
#             agreed_count = answer['agreed_count']
#             if answer_id not in all_answers:
#                 all_answers[answer_id] = agreed_count
#             else:
#                 all_answers[answer_id] += agreed_count

#     if request.is_ajax():
#         if 'interview' in request.GET:
#             return JsonResponse({'questions': questions})
#         elif 'question' in request.GET:
#             return JsonResponse({'answers': list(answers)})

#     return render(request, 'drevo/dimensional_distributions_1.html', {'interviews': interviews, 'questions': questions, 'answers': answers, 'all_answers': all_answers})


# from django.shortcuts import render
# from django.http import JsonResponse
# from drevo.models.interview_answer_expert_proposal import InterviewAnswerExpertProposal
# from drevo.views.interviews_all_view import get_interviews_all


# def dimensional_distributions_1(request):
#     category_interviews = get_interviews_all()  # получаем данные интервью
#     # получаем список имен интервью из словаря category_interviews
    
    
#     category_interview_names = [interview.name for category, interviews in category_interviews for interview in interviews]
#     interviews = list(set(InterviewAnswerExpertProposal.objects.filter(interview__is_published=True, interview__name__in=category_interview_names).values_list('interview__name', flat=True)))
#     # list_intr = get_interviews_all()
#     # interviews = list(set(InterviewAnswerExpertProposal.objects.filter(interview__is_published=True, interview__name__in=list_intr, is_agreed=True).values_list('interview__name', flat=True)))
#     questions = []
#     answers = []

#     if 'selected_interview' in request.GET:
#         selected_interview = request.GET['selected_interview']
#         questions = list(set(InterviewAnswerExpertProposal.objects.filter(question__is_published=True, interview__name=selected_interview).values_list('question__name', flat=True)))

#     if 'selected_question' in request.GET:
#         selected_question = request.GET['selected_question']
#         answers = answers = list(set(InterviewAnswerExpertProposal.objects.filter(answer__is_published=True, question__name=selected_question, is_agreed=True).values_list('answer__name', flat=True)))

#     if request.is_ajax():
#         if 'interview' in request.GET:
#             # Если это AJAX-запрос для вопросов, верните вопросы в формате JSON
#             return JsonResponse({'questions': questions})
#         elif 'question' in request.GET:
#             # Если это AJAX-запрос для ответов, верните ответы в формате JSON
#             return JsonResponse({'answers': answers})

#     return render(request, 'drevo/dimensional_distributions_1.html', {'interviews': interviews, 'questions': questions, 
#     'answers': answers})




# from django.shortcuts import render
# from django.http import JsonResponse
# from drevo.models.interview_answer_expert_proposal import InterviewAnswerExpertProposal

# def dimensional_distributions_1(request):
#     interviews = InterviewAnswerExpertProposal.objects.filter(interview__is_published=True, is_agreed=True)
#     questions = InterviewAnswerExpertProposal.objects.none()
#     answers = InterviewAnswerExpertProposal.objects.none()

#     if 'selected_interview' in request.GET:
#         selected_interview = request.GET['selected_interview']
#         questions = InterviewAnswerExpertProposal.objects.filter(question__is_published=True, interview__name=selected_interview, is_agreed=True)

#     if 'selected_question' in request.GET:
#         selected_question = request.GET['selected_question']
#         answers = InterviewAnswerExpertProposal.objects.filter(answer__is_published=True, question__name=selected_question, is_agreed=True)

#     if request.is_ajax():
#         if 'interview' in request.GET:
#             # Если это AJAX-запрос для вопросов, верните вопросы в формате JSON
#             return JsonResponse({'questions': list(questions.values())})
#         elif 'question' in request.GET:
#             # Если это AJAX-запрос для ответов, верните ответы в формате JSON
#             return JsonResponse({'answers': list(answers.values())})

#     return render(request, 'drevo/dimensional_distributions_1.html', {'interviews': interviews, 'questions': questions, 'answers': answers})
