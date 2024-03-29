from django.shortcuts import render, get_object_or_404
from drevo.models.author import Author
from drevo.models.knowledge import Znanie
from drevo.models.relation import Relation
from users.models import User, Profile
from drevo.models.category import Category



def interview_table(request, id):
    interview = get_object_or_404(Znanie, id=id)
    authors = Author.objects.all()
    categories = Category.objects.all()
    interviews_tr = Relation.objects.filter(tr__name="Состав", bz__id=interview.id)
    relations = Relation.objects.all()
    questions = Znanie.objects.filter(tz__name="Вопрос")
    
    author_list = []
    answered_authors = set()  # Создаем множество для авторов, которые дали ответы
    matrix = {}
    questions_list = []
    
    minus = "-"
    for question in questions:
        questions_rz = Relation.objects.filter(rz__name=question, bz__id=interview.id)
        for question_rz in questions_rz:
            matrix[question_rz.rz.name] = []
            questions_list.append(question_rz.rz.name) 
    for question in questions:
        questions_rz = Relation.objects.filter(rz__name=question, bz__id=interview.id)
        for question_rz in questions_rz:
            questions_bz = Relation.objects.filter(bz__name=question_rz.rz.name, tr__name="Ответ" )
            for question_bz in questions_bz:
                for author in authors:
                    answers = Relation.objects.filter(tr__name="Ответ", bz__name=question_bz.bz.name)
                    if answers:
                        for answer in answers:
                            if question_bz.bz.name in matrix:
                                if answer is not None and answer.rz.author.name == author.name:
                                    if answer not in matrix[question_bz.bz.name]:
                                        matrix[question_bz.bz.name].append(answer)
                                        answered_authors.add(author)  # Добавляем автора в множество
                                        if minus in matrix[question_bz.bz.name]:
                                            matrix[question_bz.bz.name].remove(minus)

    # формируем author_list только с авторами, которые дали ответы
    for author in answered_authors:
        profiles = Profile.objects.filter(user=author.user_author)
        for profile in profiles:
            if profile.patronymic != None:
                short_fst_name = author.user_author.first_name[0]
                short_patr = profile.patronymic[0]
                author_list.append({"name": f"{short_fst_name}.{short_patr}.{author.user_author.last_name}", "author": author})
            else:
                short_fst_name = author.user_author.first_name[0]
                author_list.append({"name": f"{short_fst_name}.{author.user_author.last_name}", "author": author})


    return render(request, "drevo/interview_table.html", {
        'authors': authors, 'matrix': matrix, 
        'questions_list': questions_list, 'questions_tr': questions_rz, 'questions_bz': questions_bz, 
        'answers': answers, 
        'author_list': author_list, 'answered_authors': answered_authors,
        'interview_this': interview, 'minus': minus
    })

    # interview = get_object_or_404(Znanie, id=id)
    # authors = Author.objects.all()
    # interview_this = interview
    # categories = Category.objects.all()
    # interviews_tr = Relation.objects.filter(tr__name="Состав", bz__id=interview.id)
    # relations = Relation.objects.all()
    # questions = Znanie.objects.filter(tz__name="Вопрос")
    
    # author_list = []
    # answered_authors = set()  # Создаем множество для авторов, которые дали ответы
    # matrix = {}
    # questions_list = []
    # minus = "-"
    # for question in questions:
    #     questions_rz = Relation.objects.filter(rz__name=question, bz__id=interview.id)
    #     for question_rz in questions_rz:
    #         matrix[question_rz.rz.name] = []
    #         questions_list.append(question_rz.rz.name) 
    
    # for question in questions:
    #     questions_rz = Relation.objects.filter(rz__name=question, bz__id=interview.id)
    #     for question_rz in questions_rz:
    #         questions_bz = Relation.objects.filter(bz__name=question_rz.rz.name, tr__name="Ответ" )
    #         for question_bz in questions_bz:
    #             for author in authors:
    #                 has_answer = False
    #                 answers = Relation.objects.filter(tr__name="Ответ", bz__name=question_bz.bz.name)
    #                 if answers:
    #                     answered_authors.add(author)  # Добавляем автора в множество
    #                     for answer in answers:
    #                         if question_bz.bz.name in matrix:
                                
    #                             if answer is not None and answer.rz.author.name == author.name:
    #                                 if answer not in matrix[question_bz.bz.name]:
    #                                     matrix[question_bz.bz.name].append(answer)
    #                                     print(answer.rz.name)
    #                                     has_answer = True
    #                             elif answer.rz.author.name != author.name:
    #                                 if minus not in matrix[question_bz.bz.name]:
    #                                     matrix[question_bz.bz.name].append(minus)
        


    # # формируем author_list только с авторами, которые дали ответы
    # for author in answered_authors:
    #     profiles = Profile.objects.filter(user=author.user_author)
    #     for profile in profiles:
    #         if profile.patronymic != None:
    #             short_fst_name = author.user_author.first_name[0]
    #             short_patr = profile.patronymic[0]
    #             author_list.append({"name": f"{short_fst_name}.{short_patr}.{author.user_author.last_name}", "author": author})
    #         else:
    #             short_fst_name = author.user_author.first_name[0]
    #             author_list.append({"name": f"{short_fst_name}.{author.user_author.last_name}", "author": author})

    # return render(request, "drevo/interview_table.html", {
    #     'authors': authors, 'matrix': matrix, 
    #     'questions_list': questions_list, 'questions_tr': questions_rz, 'questions_bz': questions_bz, 'answers': answers, 
    #     'author_list': author_list,
    #     'interview_this': interview_this, 'minus': minus
    # })
                    # for author in authors:
                #     answers = Relation.objects.filter(tr__name="Ответ", bz__name=question_bz.bz.name)
                #     if answers:
                #         answered_authors.add(author)  # Добавляем автора в множество
                #         for answer in answers:
                #             if question_bz.bz.name in matrix:
                #                 print(answer.rz.author.name)
                #                 if answer is not None and answer.rz.author.name == author.name:
                #                     if answer not in matrix[question_bz.bz.name]:
                #                         matrix[question_bz.bz.name].append(answer)
                #                 else:
                #                     if minus not in matrix[question_bz.bz.name]:
                #                         matrix[question_bz.bz.name].append(minus)

# def interview_table(request, id):
#     interview = get_object_or_404(Znanie, id=id)
#     authors = Author.objects.all()
#     interview_this = interview
#     categories = Category.objects.all()
#     interviews_tr = Relation.objects.filter(tr__name="Состав", bz__id=interview.id)
#     relations = Relation.objects.all()
#     questions = Znanie.objects.filter(tz__name="Вопрос")
    
#     author_list = []
#     for author in authors:
#         profiles = Profile.objects.filter(user=author.user_author)
#         for profile in profiles:
#             if profile.patronymic != None:
#                 short_fst_name = author.user_author.first_name[0]
#                 short_patr = profile.patronymic[0]
                
#                 author_list.append({"name": f"{short_fst_name}.{short_patr}.{author.user_author.last_name}", "author": author})
#                 print(short_fst_name, short_patr, author.user_author.last_name)
#             else:
#                 short_fst_name = author.user_author.first_name[0]
#                 author_list.append({"name": f"{short_fst_name}.{author.user_author.last_name}", "author": author})

#     matrix = {}
#     questions_list = []
#     for question in questions:
#         questions_rz = Relation.objects.filter(rz__name=question, bz__id=interview.id)
#         for question_rz in questions_rz:
#             matrix[question_rz.rz.name] = []
#             questions_list.append(question_rz.rz.name) 

#     for question in questions:
#         questions_rz = Relation.objects.filter(rz__name=question, bz__id=interview.id)
#         for question_rz in questions_rz:
#             questions_bz = Relation.objects.filter(bz__name=question_rz.rz.name, tr__name="Ответ" )
#             for question_bz in questions_bz:
#                 for author in author_list:
#                     answers = Relation.objects.filter(tr__name="Ответ", bz__name=question_bz.bz.name, author__id=author["author"].id)
#                     if answers:
#                         for answer in answers:
#                             if question_bz.bz.name in matrix:
#                                 if answer not in matrix[question_bz.bz.name]:
#                                     matrix[question_bz.bz.name].append(answer)
#                                     print(answer.rz.name)


#     return render(request, "drevo/interview_table.html", {
#         'authors': authors, 'matrix': matrix, 
#         'questions_list': questions_list, 'questions_tr': questions_rz, 'questions_bz': questions_bz, 'answers': answers, 
#         'author_list': author_list,
#         'interview_this': interview_this,
#     })

# def interview_table(request, id):
#     interview = get_object_or_404(Znanie, id=id)
#     authors = Author.objects.all()
#     experts = User.objects.filter(is_expert=True)
#     interview_this = interview
#     print(interview_this, 'blah')
#     categories = Category.objects.all()
#     interviews_tr = Relation.objects.filter(tr__name="Состав", bz__id=interview.id)
#     relations = Relation.objects.all()
#     questions = Znanie.objects.filter(tz__name="Вопрос")
    
    
#     author_list = []
#     # Проходим по всем авторам
#     for author in authors:
#         # Получаем профиль каждого автора
#         profiles = Profile.objects.filter(user=author.user_author)
#         for profile in profiles:
#             # Если у автора есть отчество
#             if profile.patronymic != None:
#                 # Получаем первую букву имени и отчества
#                 short_fst_name = author.user_author.first_name[0]
#                 short_patr = profile.patronymic[0]
#                 # Добавляем в список авторов
#                 author_list.append({"name": f"{short_fst_name}.{short_patr}.{author.user_author.last_name}", "author": author})
#                 print(short_patr, short_fst_name, author.user_author.last_name)

#             else:
#                 # Если у автора нет отчества, то получаем только первую букву имени
#                 short_fst_name = author.user_author.first_name[0]
#                 # Добавляем в список авторов
#                 author_list.append({"name": f"{short_fst_name}.{author.user_author.last_name}", "author": author})
#     matrix = {}
#     questions_list = []  # Создаем список для хранения вопросов
#     for question in questions:
#         questions_rz = Relation.objects.filter(rz__name=question, bz__id=interview.id)
#         for question_rz in questions_rz:
#             # print(question_rz.rz.name)
#             matrix[question_rz.rz.name] = []
#             questions_list.append(question_rz.rz.name) 

#         # print(question.name)
#         questions_bz = Relation.objects.filter(bz__name=question.name, tr__name="Ответ" )
#         for question_bz in questions_bz:
#             print(question_bz.bz.name)
#             answered_authors = set(answer.rz.author.name for question, answers in matrix.items() for answer in answers)
#             for author in authors:
#                 # print(expert.username)
#                 answers = Relation.objects.filter(tr__name="Ответ", bz__id=question_bz.id, rz__author__id=author.id)
                
#                 if answers:
#                     for answer in answers:
#                         print(answer.rz.name)

#                         # print(answer.rz.name)
#                         # if answer not in matrix[question_bz.bz.name]:  # Если вопрос соответствует ответу
#                         matrix[question_bz.bz.name].append(answer)


#     return render(request, "drevo/interview_table.html", {
#         'authors': authors, 'matrix': matrix, 
#         'questions_list': questions_list, 'questions_tr': questions_rz, 'questions_bz': questions_bz, 'answers': answers, 
#         'author_list': author_list,

#         'experts': experts, 'answered_authors': answered_authors,'interview_this': interview_this,
#     })
