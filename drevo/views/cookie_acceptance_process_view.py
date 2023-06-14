from django.http import Http404, JsonResponse
from django.views.generic.edit import ProcessFormView
from loguru import logger

from users.models import User

logger.add('logs/main.log',
           format="{time} {level} {message}", rotation='100Kb', level="ERROR")


class CookieAcceptance(ProcessFormView):
    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            user = self.request.user

            if user.is_authenticated:
                current_user = User.objects.get(id=user.id)
                current_user.cookie_acceptance = True
                current_user.save()
                return JsonResponse({}, status=200)

        raise Http404
