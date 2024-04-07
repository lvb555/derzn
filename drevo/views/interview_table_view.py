from collections import defaultdict
from django.shortcuts import render, get_object_or_404
from drevo.models.author import Author
from drevo.models.knowledge import Znanie
from drevo.models.relation import Relation
from users.models import User

def interview_table(request, id):
    interview = get_object_or_404(Znanie, id=id)
    interview_this = interview
    # Получаем связи с типом связи "Состав"
    questions = Relation.objects.filter(tr__name="Состав", bz__id=interview.id)
    # Создаем список для хранения вопросов
    questions_list = [question.rz.name for question in questions]
    # Создаем defaultdict для хранения авторов и их ответов.
    authors_dict = defaultdict(lambda: defaultdict(list))
    # defaultdict для И.О.Фамилии
    author_names = defaultdict(str)

    for question in questions:
        # Получаем связи с типом связи "Ответ"
        answers = Relation.objects.filter(tr__name="Ответ", bz__id=question.rz.id).select_related('rz__author').all()
        for answer in answers:
            author = answer.rz.author
            authors_dict[author.name][question.rz.name].append(answer.rz.name)

            if author.user_author.patronymic:
                short_fst_name = author.user_author.first_name[0]
                short_patr = author.user_author.patronymic[0]
                author_names[author.name] = f"{short_fst_name}.{short_patr}.{author.user_author.last_name}"
            else:
                short_fst_name = author.user_author.first_name[0]
                author_names[author.name] = f"{short_fst_name}.{author.user_author.last_name}"

    # Создаем таблицу-матрцу
    table = [[""] + questions_list]
    for author, answers in authors_dict.items():
        if answers:
            # Ряд автора и его ответов на вопросы
            row = [author_names[author]]
            for question in questions_list:
                if question in answers and answers[question]:
                    row.append(", ".join(answers[question]))
                else:
                    # Если нет ни одного ответа добавляем "-"
                    row.append("-")
            table.append(row)

    return render(request, "drevo/interview_table.html", {
        'table': table, 'interview_this': interview_this
    })
