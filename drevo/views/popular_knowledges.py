from django.shortcuts import render
from drevo.models import Znanie, BrowsingHistory, visits
from django.db.models import Count
from ..models.user_parameters import UserParameters


def get_popular_knowledges(request):
    context = {}
    template_name = 'drevo/popular_knowledges.html'
    req_data = request.POST
    if request.user.is_authenticated:
        param_names = ('Показывать просмотренные знания?', 'Порог популярности')
        fields_by_param = {
            'Порог популярности': 'record_count',
            'Показывать просмотренные знания?': 'already_seen'
        }

        params = UserParameters.objects.select_related('param').filter(user=request.user, param__name__in=param_names)

        cur_params = {
            'already_seen': 1 if 'already_seen' in req_data else 0,
            'record_count': int(req_data.get('record_count')) if 'record_count' in req_data else UserParameters.objects
            .get(param__name='Порог популярности', user=request.user).param_value
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

        if cur_params['already_seen'] == 1:
            have_seen = list(BrowsingHistory.objects.filter(user=request.user).values_list('znanie__pk', flat=True))
            all_znania = all_znania.exclude(pk__in=have_seen)
        context = {
            'all_knowledges': all_znania.annotate(count_visits=Count('visits')).order_by(
                '-count_visits')[:cur_params['record_count']],
            'record_count': cur_params['record_count'],
            'already_seen': cur_params['already_seen']
        }
    else:
        context['all_knowledges'] = Znanie.objects.filter(is_published=True, tz__is_systemic=False).order_by(
            '-visits')[:10]

    return render(request, template_name, context)
