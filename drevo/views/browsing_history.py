from django.views.generic import ListView
from drevo.models.knowledge import Znanie
from loguru import logger
from django.shortcuts import redirect

from ..models import BrowsingHistory, Comment

logger.add('logs/main.log',
    format="{time} {level} {message}", rotation='100Kb', level="ERROR")


class BrowsingHistoryListView(ListView):
    """
    Выводит список просмотренных знаний
    """
    
    model = BrowsingHistory
    context_object_name = 'browsing_history'
    template_name = 'drevo/browsing_history.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated == False:
            return redirect('/users/login')

    def get_context_data(self, *, object_list=None, **kwargs):
        """
        Контекст, передаваемый в шаблон
        """
        context = super().get_context_data(**kwargs)

        # получаем список просмотров текущего пользователя
        browsing_history_by_user = BrowsingHistory.objects.filter(user=self.request.user).order_by('-date')
        history = []

        # получаем комментарии
        for item in browsing_history_by_user:
            if item.znanie.is_published:
                obj = {}
                obj["znanie"] = item.znanie
                    
                history.append(obj)

        context['history'] = history

        return context
