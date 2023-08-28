from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.decorators.http import require_http_methods
from django.views.generic import ListView

from users.models import User
from users.views import access_sections
from ..models import UserParameters, ParameterCategories, FriendsInviteTerm, Message
from ..models.feed_messages import FeedMessage


class ParameterSettingsView(LoginRequiredMixin, ListView):
    """
        Страница "Настройки параметров"
    """
    model = UserParameters
    template_name = 'drevo/parameter_settings.html'
    context_object_name = 'settings'
    login_url = reverse_lazy('login')

    def get_queryset(self):
        params = UserParameters.objects.select_related('param').filter(user=self.request.user)
        if filter_by := self.request.GET.get('filter'):
            return params.filter(param__category__name=filter_by)
        return params

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ParameterSettingsView, self).get_context_data(**kwargs)
        context['categories'] = (
            ParameterCategories.objects.filter(params__admin=False).values_list('name', flat=True).distinct()
        )
        context['cur_filter'] = self.request.GET.get('filter')
        user = get_object_or_404(User, id=self.request.user.id)
        context['pub_user'] = user
        context['sections'] = access_sections(user)
        context['activity'] = [i for i in context['sections'] if i.startswith('Мои') or
                               i.startswith('Моя')]
        context['link'] = 'users:myprofile'
        invite_count = len(FriendsInviteTerm.objects.filter(recipient=user.id))
        context['invite_count'] = invite_count if invite_count else 0
        context['new_knowledge_feed'] = FeedMessage.objects.filter(recipient=user, was_read=False).count()
        context['new_messages'] = Message.objects.filter(recipient=user, was_read=False).count()
        context['new'] = int(context['new_knowledge_feed']) + int(
            context['invite_count'] + int(context['new_messages']))
        return context


@login_required
@require_http_methods(['POST'])
def update_user_settings(request):
    """
        Обновление и сброс настроек пользователя
    """
    post_data = {
        int(param_name.split('_')[1]): value
        for param_name, value in request.POST.items() if param_name != 'csrfmiddlewaretoken'
        and param_name != 'save_changes' and param_name != 'reset_settings'and param_name != 'reset_settings'
    }
    updated_settings = list()
    user_settings = UserParameters.objects.select_related('param').filter(user=request.user)

    if 'save_changes' in request.POST:
        # Код для сохранения изменений
        for setting in user_settings:
            new_param = post_data.get(setting.pk)
            if new_param == 'on':
                new_param = 1
            if not new_param and setting.param.is_bool:
                setting.param_value = 0
            elif not new_param:
                setting.param_value = setting.param.default_param
            elif int(new_param) != setting.param_value:
                setting.param_value = int(new_param)
            else:
                continue
            updated_settings.append(setting)

    elif 'reset_settings' in request.POST:
        # Код для сброса настроек
        for setting in user_settings:
            setting.param_value = setting.param.default_param
            updated_settings.append(setting)

    UserParameters.objects.bulk_update(updated_settings, ['param_value'])
    return redirect('parameter_settings')
