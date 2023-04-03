from functools import reduce
from operator import or_

from django.db.models import Q, F
from django.shortcuts import render, redirect
from drevo.models import UserParameters, Znanie


def search_by_tree_view(request):
    """
        Страница поиска по дереву
    """
    req_data = request.POST
    is_default_search = True if 'default_search' in req_data else False
    search_word = req_data.get('search_word')
    knowledge_pk = req_data.get('knowledge_from_tree').split(',')
    knowledge_queryset = Znanie.objects.filter(pk__in=knowledge_pk)

    def get_user_search_params() -> list:
        """
            Функция для получения параметров пользователя для поиска
        """
        user = request.user
        param_names = (
            'Искать в поле "Содержание"', 'Искать в поле "Комментарий к источнику"'
        )
        params = (
            UserParameters.objects.select_related('param')
            .filter(user=user, param__name__in=param_names)
            .values(name=F('param__name'), value=F('param_value'))
        )
        fields_by_param = {'Искать в поле "Содержание"': 'content', 'Искать в поле "Комментарий к источнику"': 'source_com'}
        for param in params:
            if not param.get('value'):
                del fields_by_param[param.get('name')]
        return list(fields_by_param.values())

    def base_filter_queryset(queryset):
        filter_fields = ['name'] + get_user_search_params()
        filter_query = reduce(or_, [Q(**{f'{field}__icontains': search_word}) for field in filter_fields])
        if is_default_search:
            return queryset.filter(filter_query)

    def advanced_filter_queryset(queryset):
        ''

    if is_default_search:
        filtered_queryset = base_filter_queryset(knowledge_queryset)
    else:
        filtered_queryset = advanced_filter_queryset(knowledge_queryset)

    if not filtered_queryset and is_default_search:
        return redirect(f"{request.META['HTTP_REFERER']}?empty_result=True")

    context = {'search_knowledge': filtered_queryset, 'search_word': search_word}
    return render(request, 'drevo/search_by_tree.html', context)
