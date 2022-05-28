from django.views.generic import ListView
from drevo.models.knowledge import Znanie
from loguru import logger
from django.http import HttpResponseNotFound

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

    def get_context_data(self, *, object_list=None, **kwargs):
        """
        Контекст, передаваемый в шаблон
        """

        context = super().get_context_data(**kwargs)

        if not self.request.user.is_authenticated:
            context['history'] = []
            return context

        # получаем список просмотров текущего пользователя
        browsing_history_by_user = BrowsingHistory.objects.filter(user=self.request.user)
        history = []

        # получаем комментарии
        for item in browsing_history_by_user:
            obj = {}
            obj["znanie"] = item.znanie

            comments = Comment.objects.filter(author=self.request.user, znanie=item.znanie)
            obj["comments"] = comments
            history.append(obj)

        context['history'] = history

        return context
