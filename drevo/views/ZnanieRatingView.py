from django.http import Http404, JsonResponse
from django.views.generic.edit import ProcessFormView
from ..models import Znanie, ZnRating
from ..models import Znanie, ZnRating
from loguru import logger


logger.add('logs/main.log',
           format="{time} {level} {message}", rotation='100Kb', level="ERROR")


class ZnanieRatingView(ProcessFormView):
    def get(self, request, pk, vote, *args, **kwargs):
        if request.is_ajax():
            if not self.request.user.is_authenticated:
                return JsonResponse({}, status=403)

            if pk and vote:
                if vote in (ZnRating.LIKE, ZnRating.DISLIKE):
                    znanie = Znanie.objects.get(pk=pk)
                    znanie.voting(self.request.user, vote)
                    return JsonResponse({}, status=200)

        raise Http404
