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


def search_node_categories(categories_expert):
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
        for category_child in list_level[category_expert.level :]:
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


def get_tree(obj, user):
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

    categories = search_node_categories(categories_expert)

    tz_id = Tz.objects.get(name="Интервью").id
    zn_list = Znanie.objects.filter(tz_id=tz_id, is_published=True)
    tr_period = Tr.objects.get(name="Период интервью").id
    now = datetime.datetime.now()

    def reg_collector(sub):
        """
        Обрабатывает варианты написания даты в Период интервью
        Выводим delta - разница между первой даты и второй
        Выводим from_ и before - дата от и до
        """
        one_day = datetime.timedelta(days=1)
        regex_all = "(\\d+)\\s*\\S\\s*(\\d+)\\s*\\S\\s*(\\d+)\\s*\\S\\s*(\\d+)\\s*\\S\\s*(\\d+)\\s*\\S\\s*(\\d+)"
        regex_from = "(\\d+)\\s*\\S\\s*(\\d+)\\s*\\S\\s*(\\d+)\\s*(\\-)\\s*"
        regex_to = "(\\-)\\s*(\\d+)\\s*\\S\\s*(\\d+)\\s*\\S\\s*(\\d+)"
        regex_list = re.findall(regex_all, sub.name)
        re_from = re.findall(regex_from, sub.name)
        re_to = re.findall(regex_to, sub.name)

        def condition_period(operand):
            bool_less = now < operand
            if bool_less:
                day = operand + one_day
                return day
            else:
                day = now + one_day
                return day

        if regex_list:
            resultat_re = regex_list
            regex = regex_all
            from_sub = re.sub(regex, "20\\3", sub.name, 0, re.MULTILINE)
            after_sub = re.sub(regex, "20\\6", sub.name, 0, re.MULTILINE)
            from_ = datetime.datetime(
                int(from_sub), int(resultat_re[0][1]), int(resultat_re[0][0])
            )
            before = datetime.datetime(
                int(after_sub), int(resultat_re[0][-2]), int(resultat_re[0][-3])
            )
        elif re_to:
            resultat_re = re_to
            after_sub = re.sub(regex_to, "20\\4", sub.name, 0, re.MULTILINE)
            before = datetime.datetime(
                int(after_sub), int(resultat_re[0][2]), int(resultat_re[0][1])
            )
            from_ = now
        else:
            resultat_re = re_from
            from_sub = re.sub(regex_from, "20\\3", sub.name, 0, re.MULTILINE)
            from_ = datetime.datetime(
                int(from_sub), int(resultat_re[0][1]), int(resultat_re[0][0])
            )
            before = condition_period(from_)

        delta_from = now - from_
        delta_before = now - before
        return delta_from, delta_before

    def collector_dict_period(znanies, dict_period):
        """
        Собирает в словарь период и проверяет условие: сегодня в периоде?
        """
        for zn in znanies:
            try:
                periods_r = zn.base.filter(tr_id=tr_period, is_published=True)[0]
                period = Znanie.objects.filter(is_published=True, id=periods_r.rz_id)[0]
                delta_from, delta_after = reg_collector(period)
                if delta_from.days >= 0 and delta_after.days <= 0:
                    dict_period[zn.name] = [period, True]
                else:
                    dict_period[zn.name] = [period, False]
            except IndexError:
                pass
        return dict_period

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

    def my_answer(list_answer):
        """
        Считает ответы эксперта на вопросы
        """
        counter = 0
        for answer in list_answer:
            author_answer = Znanie.objects.get(
                is_published=True, id=answer.rz_id
            ).author_id
            try:
                author = Author.objects.filter(id=author_answer)[0]
                author = author.name
            except IndexError:
                author = "None"
            if user.username == author:
                counter += 1
        return counter

    def generator_interview(category, dict_elements):
        """
        Генерация интервью и проверка условия для исключения категории
        """
        for interview in dict_elements[category]:
            yield interview

    def generator_key(list_key):
        """
        Генератор ключей - категории
        """
        for key in list_key:
            yield key

    def generator_question(obj_quest_list):
        """
        Генерация вопросов
        """
        for obj in obj_quest_list:
            relation_qi = Znanie.objects.get(is_published=True, id=obj.rz_id)
            yield relation_qi

    relation_dict = {}
    # Формируем словарь {Интервью: [ответы экспертов, на все вопросы ответили?, Эксперт ответил на все вопросы?]}
    # Добавляем в словарь с категориями количество ответов Эксперта
    for category in generator_key(zn_dict.keys()):
        for interview in generator_interview(category, zn_dict):
            number_answer = 0
            relation_obj = interview.base.filter(tr_id=obj_interview, is_published=True)
            for relation_qi in generator_question(relation_obj):
                relation_answer = relation_qi.base.filter(
                    tr_id=tr_answer, is_published=True
                )
                quantity_answer = my_answer(relation_answer)
                number_answer += quantity_answer
            try:
                if number_answer == len(relation_obj) and number_answer:
                    relation_dict[interview.name] = [len(relation_obj), True]
                else:
                    relation_dict[interview.name] = [len(relation_obj), False]
            except KeyError:
                pass
    # Подставляем список периода в словарь к каждому существующему интервью
    for key, value in relation_dict.items():
        try:
            true_period = period_dict[key]
            value.append(true_period)
        except KeyError:
            value.append(False)
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