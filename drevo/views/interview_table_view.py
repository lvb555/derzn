from collections import defaultdict
from django.shortcuts import render, get_object_or_404
from drevo.models.knowledge import Znanie
from drevo.models.relation import Relation

def interview_table(request, id):
    interview = get_object_or_404(Znanie, id=id)
    interview_this = interview
    questions = Relation.objects.filter(tr__name="Состав", bz__id=interview.id)
    question_list = [question.rz for question in questions]
    authors_dict = defaultdict(lambda: defaultdict(list))
    author_names = defaultdict(str)
    answers = Relation.objects.filter(tr__name="Ответ", bz__in=question_list).select_related('rz__author').all()
    for question in questions:
        for answer in answers:
            if answer.bz.id == question.rz.id:
                author = answer.rz.user
                authors_dict[author.id][question.rz].append(answer.rz.name)
                if answer.rz.user.patronymic:
                    short_fst_name = answer.rz.user.first_name[0]
                    short_patr = answer.rz.user.patronymic[0]
                    author_names[author.id] = f"{short_fst_name}.{short_patr}.{answer.rz.user.last_name}"
                else:
                    short_fst_name = author.first_name[0]
                    author_names[author.id] = f"{short_fst_name}.{answer.rz.user.last_name}"

    table = [[""] + question_list]
    for author_id, answers in authors_dict.items():
        if answers:
            row = [author_names[author_id]]
            for question in question_list:
                if question in answers and answers[question]:
                    row.append(", ".join(answers[question]))
                else:
                    row.append("-")
            table.append(row)

    return render(request, "drevo/interview_table.html", {
        'table': table, 'interview_this': interview_this
    })