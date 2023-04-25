from django.shortcuts import redirect, render, get_object_or_404
from drevo.models.author import Author

from drevo.models.knowledge import Znanie
from drevo.models.knowledge_kind import Tz
from drevo.models.relation_type import Tr
from drevo.models.special_permissions import SpecialPermissions


def interview_view(request, pk):
    """
    Отображаем страницу Интервью
    """
    expert = SpecialPermissions.objects.filter(expert=request.user)
    if expert.exists():
        context = get_list_question(pk, request.user)
        return render(request, 'drevo//interview_page.html', context)
    return redirect('/drevo/')


def get_list_question(pk, user):
    """
    Получаем контекст
    znanie - для отображения верхней части, как и у обычного знания
    question - список вопросов интервью
    q_true - у вопросов интервью отображаются ответы эксперта на вопросыы
    """
    context = {}
    interview = Znanie.objects.get(id=pk)
    context['znanie'] = interview

    tz_id = Tz.objects.get(name='Вопрос').id
    question_zn = Znanie.objects.filter(tz_id=tz_id, is_published=True).order_by('-order')
    list_d = []
    for zn in question_zn:
        relation = zn.related.all()
        if not relation:
            continue
        need_interview = relation[0].bz_id
        if need_interview == interview.id:
            list_d.append(zn)
    tr_answer = get_object_or_404(Tr, name='Ответ').id
    dict_q = {}
    for q in list_d:
        relation_answer = q.base.filter(tr_id=tr_answer, is_published=True)
        if not relation_answer:
            dict_q[q] = False
            continue
        for answer in relation_answer:
            author_answer = Znanie.objects.get(id=answer.rz_id, is_published=True).author_id
            try:
                author = Author.objects.filter(id=author_answer)[0]
                author = author.name
            except IndexError:
                author = 'None'
            if user.username == author:
                dict_q[q] = True
                break
            dict_q[q] = False
    
    def filter_true_false(dict_before, dict_after, bool=True):
        for key, value in dict_before.items():
            if value == bool:
                dict_after[key] = value

    result_dict = {}
    filter_true_false(dict_q, result_dict)
    filter_true_false(dict_q, result_dict, False)
    
    context['q_true'] = result_dict
    return context