from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic.edit import ProcessFormView

from users.models import Favourite
from drevo.models import Znanie
from loguru import logger


logger.add('logs/main.log',
           format="{time} {level} {message}", rotation='100Kb', level="ERROR")


class FavouriteProcessView(ProcessFormView):
    def get(self, request, pk):
        if request.is_ajax():
            if not self.request.user.is_authenticated:
                return JsonResponse({}, status=403)

            znanie = get_object_or_404(Znanie, id=pk)
            user_favourite = Favourite.objects.get_or_create(user=request.user)[0]
            if user_favourite.favourites.filter(id=pk).exists():
                user_favourite.favourites.remove(znanie)
            else:
                user_favourite.favourites.add(znanie)

            return JsonResponse({}, status=200)

        raise Http404
