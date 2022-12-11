from django.shortcuts import get_object_or_404
from django.http import Http404, JsonResponse
from django.views.generic.edit import ProcessFormView
from ..models import Znanie, QuizResult
from loguru import logger
import json

logger.add('logs/main.log',
           format="{time} {level} {message}", rotation='100Kb', level="ERROR")


class QuizResultAdd(ProcessFormView):
    def get(self, request, pk, *args, **kwargs):
        if request.is_ajax():
            user = self.request.user

            if not user.is_authenticated:
                return JsonResponse({}, status=403)

            if pk:
                quiz = get_object_or_404(Znanie, id=pk)
                QuizResult.objects.filter(user=user, quiz=quiz).delete()
                dict_ = json.loads(request.GET.get('values'))
                for a, b in dict_.items():
                    for i in b:
                        question = get_object_or_404(Znanie, id=int(a))
                        answer = get_object_or_404(Znanie, id=int(i))
                        QuizResult.objects.create(
                            quiz=quiz,
                            question=question,
                            user=user,
                            answer=answer,
                        )

                return JsonResponse({}, status=200)

        raise Http404
