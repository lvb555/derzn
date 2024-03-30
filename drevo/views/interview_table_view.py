from django.shortcuts import render, get_object_or_404
from drevo.models.author import Author
from drevo.models.knowledge import Znanie
from drevo.models.relation import Relation
from users.models import User, Profile


def interview_table(request, id):
    interview = get_object_or_404(Znanie, id=id)
    interview_this = interview
    authors = Author.objects.all()
    # Получаем связи с типом связи "Состав"
    questions = Relation.objects.filter(tr__name="Состав", bz__id=interview.id)

    # Создаем словарь для хранения вопросов
    questions_dict = {question.rz.name: question.rz.name for question in questions}

    # Создаем словарь для хранения авторов и их ответов.
    authors_dict = {}
    # Словарь для И.О.Фамилии
    author_names = {}

    for author in authors:
        authors_dict[author.name] = {}
        for question in questions:
            # Получаем связи с типом связи "Ответ"
            answers = Relation.objects.filter(tr__name="Ответ", rz__author=author, bz__name=question.rz.name)
            if answers:
                authors_dict[author.name][question.rz.name] = [answer.rz.name for answer in answers]
                profile = Profile.objects.get(user=author.user_author)
                if profile.patronymic:
                    short_fst_name = author.user_author.first_name[0]
                    short_patr = profile.patronymic[0]
                    author_names[author.name] = f"{short_fst_name}.{short_patr}.{author.user_author.last_name}"
                else:
                    short_fst_name = author.user_author.first_name[0]
                    author_names[author.name] = f"{short_fst_name}.{author.user_author.last_name}"

    # Создаем таблицу-матрцу
    table = [[""] + list(questions_dict.keys())]
    for author, answers in authors_dict.items():
        if answers:
            # Ряд автора и его ответов на вопросы
            row = [author_names[author]]
            for question in questions_dict.keys():
                if question in answers and answers[question]:
                    row.append(", ".join(answers[question]))
                else:
                    # Если нет ни одного ответа добавляем "-"
                    row.append("-")
            table.append(row)

    return render(request, "drevo/interview_table.html", {
        'table': table, 'interview_this': interview_this
    })


# from django.shortcuts import render, get_object_or_404
# from drevo.models.author import Author
# from drevo.models.knowledge import Znanie
# from drevo.models.relation import Relation
# from users.models import User, Profile
# from drevo.models.category import Category



# def interview_table(request, id):
#     interview = get_object_or_404(Znanie, id=id)
#     authors = Author.objects.all()
#     questions = Relation.objects.filter(tr__name="Состав")

#     # Create a dictionary to store the questions
#     questions_dict = {question.rz.name: question.rz.name for question in questions}
#     for question_dict in questions_dict:
#         print(question_dict)
#     # Create a dictionary to store the authors and their answers
#     authors_dict = {}
#     for author in authors:
#         answers = Relation.objects.filter(tr__name="Ответ", rz__author=author)
#         authors_dict[author.name] = {answer.bz.name: answer.rz.name for answer in answers if answer.bz.name in questions_dict}

#     # Create a table-matrix
#     table = [[""] + list(questions_dict.keys())]
#     for author, answers in authors_dict.items():
#         row = [author]
#         for question in questions_dict.keys():
#             if question in answers:
#                 row.append(answers[question])
#             else:
#                 row.append("-")
#         table.append(row)

#     return render(request, "drevo/interview_table.html", {
#         'table': table, 'interview': interview
#     })

# from django.shortcuts import render, get_object_or_404
# from drevo.models.author import Author
# from drevo.models.knowledge import Znanie
# from drevo.models.relation import Relation
# from users.models import User, Profile
# from drevo.models.category import Category



# def interview_table(request, id):
#     interview = get_object_or_404(Znanie, id=id)
#     authors = Author.objects.all()
#     categories = Category.objects.all()
#     interviews_tr = Relation.objects.filter(tr__name="Состав", bz__id=interview.id)
#     relations = Relation.objects.all()
#     questions = Znanie.objects.filter(tz__name="Вопрос")
    
#     author_list = []
#     answered_authors = set()  # Создаем множество для авторов, которые дали ответы
#     matrix = {}
#     questions_list = []
    
#     minus = "-"
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
#                 for author in authors:
#                     answers = Relation.objects.filter(tr__name="Ответ", bz__name=question_bz.bz.name)
#                     if answers:
#                         for answer in answers:
#                             if question_bz.bz.name in matrix:
#                                 if answer is not None and answer.rz.author.name == author.name:
#                                     if answer not in matrix[question_bz.bz.name]:
#                                         matrix[question_bz.bz.name].append(answer)
#                                         answered_authors.add(author)  # Добавляем автора в множество
#                                         if minus in matrix[question_bz.bz.name]:
#                                             matrix[question_bz.bz.name].remove(minus)

#     # формируем author_list только с авторами, которые дали ответы
#     for author in answered_authors:
#         profiles = Profile.objects.filter(user=author.user_author)
#         for profile in profiles:
#             if profile.patronymic != None:
#                 short_fst_name = author.user_author.first_name[0]
#                 short_patr = profile.patronymic[0]
#                 author_list.append({"name": f"{short_fst_name}.{short_patr}.{author.user_author.last_name}", "author": author})
#             else:
#                 short_fst_name = author.user_author.first_name[0]
#                 author_list.append({"name": f"{short_fst_name}.{author.user_author.last_name}", "author": author})


#     return render(request, "drevo/interview_table.html", {
#         'authors': authors, 'matrix': matrix, 
#         'questions_list': questions_list, 'questions_tr': questions_rz, 'questions_bz': questions_bz, 
#         'answers': answers, 
#         'author_list': author_list, 'answered_authors': answered_authors,
#         'interview_this': interview, 'minus': minus
#     })