from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from ..models import UserParameters


@login_required
def parameter_settings(request):
    """
        Представление для старницы настройки параметров
    """
    if request.method == 'POST':
        post_data = request.POST
        updated_settings = list()
        for param, param_value in post_data.items():
            if param == 'csrfmiddlewaretoken':
                continue
            param_pk = param.split('_')[1]
            # Если значение параметра есть, то устанавливаем его
            if param_value:
                updated_settings.append(UserParameters(pk=param_pk, param_value=param_value))
                continue
            # Если значения нет, то устанавливаем значение по умолчанию
            default_param = UserParameters.objects.select_related('param').filter(pk=param_pk).values_list(
                'param__default_param', flat=True
            ).first()
            updated_settings.append(UserParameters(pk=param_pk, param_value=default_param))
        UserParameters.objects.bulk_update(updated_settings, ['param_value'])
        return redirect('parameter_settings')

    context = dict()
    user_settings = UserParameters.objects.select_related('param').prefetch_related('param__category').filter(
        user=request.user
    )
    context['categories'] = set(user_setting.param.category.name for user_setting in user_settings)
    filter_value = request.GET.get('filter')
    if filter_value:
        context['settings'] = user_settings.filter(param__category__name=filter_value)
        context['cur_filter'] = request.GET.get('filter')
    else:
        context['settings'] = user_settings
    return render(request, 'drevo/parameter_settings.html', context=context)
