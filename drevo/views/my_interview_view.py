from django.shortcuts import redirect, render
from drevo.models.author import Author

from drevo.models.category import Category
from drevo.models.knowledge import Znanie
from drevo.models.knowledge_kind import Tz
from drevo.models.relation_type import Tr

import datetime
import re


def my_interview_view(request):
    """
    Отобажаем страницу Мои интервью
    """
    expert = request.user.expert.all()
    if expert:
        context = get_tree(expert[0], request.user)
        return render(request, "drevo//my_interview_page.html", context)
    return redirect("/drevo/")


def search_competence(categories_expert):
    """
    На ввод QuerySet категорий из таблицы CategoryExpert,
    вызывается  categories_expert = obj.categories.all(),
    где obj = request.user.expert.all()[0].
    На выходе получаем список всех категорий,
    которые относятся к эксперту.
    Пинцип работы простой:
    Из списка выбранных категорий по очереди фильтруется список категорий из одной ветки
    """
    list_category_id = []
    for category_expert in categories_expert:
        list_level = Category.objects.filter(tree_id=category_expert.tree_id)
        levels_to_process = list_level[category_expert.level :]
        for category_child in levels_to_process:
            if category_expert.level > category_child.level:
                continue
            elif category_expert.level >= category_child.level:
                list_category_id.append(category_expert.id)
            else:
                list_category_id.append(category_child.id)
    list_category_id = list(set(list_category_id))
    categories = Category.tree_objects.filter(
        is_published=True, id__in=list_category_id
    )
    return categories


def reg_collector(sub):
    """
    Обрабатывает варианты написания даты в Период интервью
    Выводим delta - разница между первой даты и второй
    Выводим from_ и before - дата от и до
    """
    regex_all = "(\\d+)\\.*\\-*(\\d+)\\.*\\-*(\\d+)\\s*\\.*\\+*\\-*\\s*(\\d+)\\.*\\-*(\\d+)\\.*\\-*(\\d+)"
    regex_before = "(\\d+)\\.*\\-*(\\d+)\.*\\-*(\\d+)(\\-*\\s*)"  # NOQA: W605
    regex_after = "(\\-*\s*)(\\d+)\\.*\\-*(\\d+)\\.*\\-*(\\d+)"  # NOQA: W605
    regex_list = re.findall(regex_all, sub.name)
    re_from = re.findall(regex_before, sub.name)
    re_before = re.findall(regex_after, sub.name)
    if len(regex_list[0]) == 6 and len(regex_list[0][1]) == 2:
        resultat_re = regex_list
        regex = regex_all
        from_sub = re.sub(regex, "20\\3", sub.name, 0, re.MULTILINE)
        after_sub = re.sub(regex, "20\\6", sub.name, 0, re.MULTILINE)
    elif re_before[0][0] == "-":
        resultat_re = re_before
        regex = regex_after
        after_sub = re.sub(regex, "20\\4", sub.name, 0, re.MULTILINE)
    else:
        resultat_re = re_from
        regex = regex_before
        from_sub = re.sub(regex, "20\\3", sub.name, 0, re.MULTILINE)
    one_day = datetime.timedelta(days=1)
    if sub.name[-1] == "-":
        from_ = datetime.datetime(
            int(from_sub), int(resultat_re[0][1]), int(resultat_re[0][0])
        )
        before = from_ + one_day
    elif sub.name[0] == "-":
        before = datetime.datetime(
            int(after_sub), int(resultat_re[0][2]), int(resultat_re[0][1])
        )
        from_ = before - one_day
    else:
        from_ = datetime.datetime(
            int(from_sub), int(resultat_re[0][1]), int(resultat_re[0][0])
        )
        before = datetime.datetime(
            int(after_sub), int(resultat_re[0][-2]), int(resultat_re[0][-3])
        )
    now = datetime.datetime.now()
    delta_from = now - from_
    delta_before = now - before
    return delta_from, delta_before, from_, before


def collector_str_period(from_, after_):
    """
    переводит дату в вид 12.06.2000-21.08.2022
    """
    from_str = from_.strftime("%d.%m.%y")
    after_str = after_.strftime("%d.%m.%y")
    result_period = from_str + "-" + after_str
    return result_period


def collector_dict_period(znanies, dict_period):
    """
    Собирает в словарь период и проверяет условие: сегодня в периоде?
    """
    tr_period = Tr.objects.get(name="Период интервью").id
    for zn in znanies:
        try:
            periods_r = zn.base.filter(tr_id=tr_period)[0]
            period = Znanie.objects.get(is_published=True, id=periods_r.rz_id)
            delta_from, delta_after, from_, after_ = reg_collector(period)
            result_period = collector_str_period(from_, after_)
            if delta_from.days >= 0 and delta_after.days <= 0:
                dict_period[zn.name] = [result_period, True]
            else:
                dict_period[zn.name] = [result_period, False]
        except IndexError:
            now = datetime.datetime.now()
            tomorrow = now + datetime.timedelta(days=1)
            yesterday = now - datetime.timedelta(days=1)
            result_period = collector_str_period(yesterday, tomorrow)
    return dict_period


def my_answer(list_answer, user):
    """
    Считает ответы эксперта на вопросы
    """
    counter = 0
    for answer in list_answer:
        author_answer = Znanie.objects.get(is_published=True, id=answer.rz_id).author_id
        try:
            author = Author.objects.filter(id=author_answer)[0]
            author = author.name
        except IndexError:
            author = "None"
        if user.username == author:
            counter += 1
    return counter


# TODO: Simplify this
def get_tree(obj, user):  # NOQA: C901
    """
    получаем context

    rt_dict:
    {'интервью': ['кол-во вопросов', 'все вопросы отвечены?', ['период', 'сегодня день в периоде?']]}

    zn_dict:
    {категория: QuerySet[список интервью]}
    """
    context = {}
    categories_expert = obj.categories.all()
    # Получаем список категорий по уровням

    categories = search_competence(categories_expert)

    tz_id = Tz.objects.get(name="Интервью").id
    zn_list = Znanie.objects.filter(tz_id=tz_id)

    zn_dict = {}
    dict_period = {}
    # Формируем словарь {"категория": QuerySet[список интервью]}
    for category in categories:
        zn_in_this_category = zn_list.filter(category=category).order_by("-date")
        if zn_in_this_category:
            period_dict = collector_dict_period(zn_in_this_category, dict_period)
        zn_dict[category] = zn_in_this_category
    zn_dict = {key: value for key, value in zn_dict.items() if len(value)}
    tr_answer = Tr.objects.get(name="Ответ [ы]").id
    obj_interview = Tr.objects.get(name="Состав").id

    relation_dict = {}
    # Формируем словарь {Интервью: [ответы экспертов, число ответов, Эксперт ответил на все вопросы?]}
    # Добавляем в словарь с категориями количество ответов Эксперта
    for category in zn_dict.keys():
        for interview in zn_dict[category]:
            number_answer = 0
            relation_obj = interview.base.filter(tr_id=obj_interview)
            for relation_qi in Znanie.objects.filter(
                is_published=True, id__in=[o.pk for o in relation_obj]
            ):
                relation_answer = relation_qi.base.filter(tr_id=tr_answer)
                quantity_answer = my_answer(relation_answer, user)
                number_answer += quantity_answer

            all_answered = number_answer == len(relation_obj)
            period_for_interview, is_today_in_period = period_dict.get(
                interview.name, ("", False)
            )
            relation_dict[interview.name] = dict(
                count=len(relation_obj),
                all_answered=all_answered,
                period=period_for_interview,
                today_in_range=is_today_in_period,
            )

    # Удаляем пустую категорию из словаря
    zn_dict_new = {}
    for key, value in zn_dict.items():
        counter = 0
        for quest in value:
            try:
                relation_dict[quest.name]
                counter += 1
                break
            except KeyError:
                counter = 0
        if counter:
            zn_dict_new[key] = value

    context["rt_dict"] = relation_dict
    context["zn_dict"] = zn_dict_new
    return context
