from datetime import date, timedelta

from django.shortcuts import render
from drevo.models import Znanie, visits, Category, Visits
from django.db.models import Count
from ..models.user_parameters import UserParameters
from ..relations_tree import get_children_for_knowledge


# Функция по возвращению потомков знаний нужной категории, чтобы найти знания, у которых категория не указана, но
# фактически принадлежащих категории
def get_unmarked_children(queryset):
    for item in queryset:
        new_queryset = get_children_for_knowledge(item)
        new_queryset = get_unmarked_children(new_queryset)
        queryset = queryset | new_queryset
    return queryset


def get_popular_knowledges(request):
    context = {}
    template_name = 'drevo/popular_knowledges.html'
    req_data = request.POST
    context['categories'] = Category.tree_objects.filter(is_published=True)
    if request.user.is_authenticated:
        param_names = ('Знания, не просмотренные мной', 'Число наиболее популярных записей')
        fields_by_param = {
            'Число наиболее популярных записей': 'record_count',
            'Знания, не просмотренные мной': 'already_seen'
        }

        params = UserParameters.objects.select_related('param').filter(user=request.user, param__name__in=param_names)

        cur_params = {
            'already_seen': 1 if 'already_seen' in req_data else 0,
            'record_count': int(req_data.get('record_count')) if 'record_count' in req_data else UserParameters.objects
            .get(param__name='Число наиболее популярных записей', user=request.user).param_value
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

        all_znania = Znanie.objects.filter(is_published=True, tz__is_systemic=False)

        date_dict = {
            'За все время': 1,
            'За день': 0,
            'За неделю': 6,
            'За месяц': 29
        }

        if req_data:
            if req_data['knowledge_category'] != '-1':
                category_and_descendants = Category.objects.get(pk=req_data['knowledge_category']).get_descendants(
                    include_self=True).filter(is_published=True)
                all_znania = all_znania.filter(category__in=category_and_descendants)
                all_znania = get_unmarked_children(all_znania)


            if req_data['date'] != '1':
                enddate = date.today()
                startdate = enddate - timedelta(days=int(req_data['date']))
                knowledges_in_timeline = Visits.objects.filter(date__range=[startdate, enddate]).values_list(
                    'znanie__pk', flat=True)
                all_znania = all_znania.filter(pk__in=knowledges_in_timeline)

        if cur_params['already_seen'] == 1:
            have_seen = list(Visits.objects.filter(user=request.user).values_list('znanie__pk', flat=True))
            all_znania = all_znania.exclude(pk__in=have_seen)
        context = {
            'all_knowledges': all_znania.annotate(count_visits=Count('visits')).order_by(
                '-count_visits')[:cur_params['record_count']],
            'record_count': cur_params['record_count'],
            'already_seen': cur_params['already_seen'],
            'knowledge_category_pk': int(req_data['knowledge_category']) if req_data else '-1',
            'categories': Category.tree_objects.filter(is_published=True),
            'date_dict': date_dict,
            'date_value': int(req_data['date']) if req_data else '1'
        }
    else:
        context['all_knowledges'] = Znanie.objects.filter(is_published=True, tz__is_systemic=False).order_by(
            '-visits')[:10]

    return render(request, template_name, context)
