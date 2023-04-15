from _operator import and_
from functools import reduce
from operator import or_

from django.db.models import Q
from django.shortcuts import render, redirect
from drevo.models import UserParameters, Znanie, SettingsOptions


def _get_user_search_params(user, req_data) -> list:
    """
        Функция для получения параметров пользователя для поиска
    """
    param_names = (
        'Искать в поле "Содержание"', 'Искать в поле "Комментарий к источнику"', 'Учитывать структурные знания'
    )
    fields_by_param = {
        'Искать в поле "Содержание"': 'content',
        'Искать в поле "Комментарий к источнику"': 'source_com',
        'Учитывать структурные знания': 'use_struct'
    }

    if user.is_anonymous:
        params = SettingsOptions.objects.filter(name__in=param_names, default_param=1, is_bool=True)
        return [fields_by_param.get(param.name) for param in params]

    params = UserParameters.objects.select_related('param').filter(user=user, param__name__in=param_names)

    cur_params = {
        'content': 1 if 'content' in req_data else 0,
        'source_com': 1 if 'source_com' in req_data else 0,
        'use_struct': 1 if 'use_struct' in req_data else 0,
    }

    updated_user_param = list()

    for user_param in params:
        param_field = fields_by_param.get(user_param.param.name)
        if cur_params.get(param_field) != user_param.param_value:
            user_param.param_value = cur_params.get(param_field)
            updated_user_param.append(user_param)
        if not user_param.param_value:
            del fields_by_param[user_param.param.name]
    if updated_user_param:
        UserParameters.objects.bulk_update(updated_user_param, ['param_value'])
    if 'Учитывать структурные знания' in fields_by_param:
        del fields_by_param['Учитывать структурные знания']
    return list(fields_by_param.values())


def search_by_tree_view(request):
    """
        Страница поиска по дереву
    """
    req_data = request.POST
    is_advance_search = True if 'advance_search' in req_data else False
    search_word = req_data.get('search_word')
    knowledge_pk = req_data.get('knowledge_from_tree').split(',')
    knowledge_queryset = Znanie.objects.filter(pk__in=knowledge_pk)

    def base_filter_queryset(queryset):
        filter_fields = ['name'] + _get_user_search_params(request.user, req_data)
        filter_query = reduce(or_, [Q(**{f'{field}__icontains': search_word}) for field in filter_fields])
        return queryset.filter(filter_query)

    if is_advance_search and not search_word:
        filtered_queryset = knowledge_queryset
    else:
        filtered_queryset = base_filter_queryset(knowledge_queryset)

    if not filtered_queryset and not is_advance_search:
        return redirect(f"{request.META['HTTP_REFERER']}?empty_result=True")

    context = {
        'search_knowledge': filtered_queryset,
        'search_word': search_word,
        'is_advance_search': is_advance_search,
        'page_title': 'Результаты поиска' if not is_advance_search else 'Расширенный поиск'
    }
    return render(request, 'drevo/search_by_tree.html', context)


def advance_search_by_tree_view(request):
    """
        Страница расширенного поиска по дереву
    """
    req_data = request.POST
    search_word = req_data.get('search_word')
    knowledge_pk = req_data.get('knowledge_from_tree').split(',')
    knowledge_queryset = Znanie.objects.prefetch_related('base').filter(pk__in=knowledge_pk)

    def advanced_filter_queryset(queryset):
        advance_fields_lookups = {
            'knowledge_type': 'tz_id__in',
            'author': 'author_id__in',
            'relation_type': 'base__tr_id__in',
            'tag': 'labels__in'
        }
        advance_filter_fields = [
            Q(**{lookup: req_data.getlist(field_name)})
            for field_name, lookup in advance_fields_lookups.items() if req_data.get(field_name)
        ]

        base_search_fields = ['name'] + _get_user_search_params(request.user, req_data)
        base_filter_fields = [Q(**{f'{field}__icontains': search_word}) for field in base_search_fields]
        if advance_filter_fields:
            filter_query = (reduce(or_, base_filter_fields) & reduce(and_, advance_filter_fields))
        else:
            filter_query = reduce(or_, base_filter_fields)
        return queryset.filter(filter_query)

    filtered_queryset = advanced_filter_queryset(knowledge_queryset)
    context = {
        'search_knowledge': filtered_queryset,
        'search_word': search_word,
        'page_title': 'Результаты расширенного поиска'
    }
    return render(request, 'drevo/search_by_tree.html', context)
