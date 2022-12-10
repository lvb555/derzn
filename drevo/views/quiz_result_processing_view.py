from django.shortcuts import get_object_or_404
from django.http import Http404, JsonResponse
from django.views.generic.edit import ProcessFormView
from ..models import Znanie, QuizResult
from users.models import User
from loguru import logger
import datetime
from django.utils.timezone import now

logger.add('logs/main.log',
           format="{time} {level} {message}", rotation='100Kb', level="ERROR")


class QuizResultAdd(ProcessFormView):
    def get(self, request, pk, *args, **kwargs):
        if request.is_ajax():
            user = self.request.user

            if not user.is_authenticated:
                return JsonResponse({}, status=403)

            if pk:
                question_pk = self.request.GET.get('question_pk')
                answer_pk = self.request.GET.get('answer_pk')
                user = get_object_or_404(User, id=user.id)
                answer = get_object_or_404(Znanie, id=answer_pk)
                quiz = get_object_or_404(Znanie, id=pk)
                question = get_object_or_404(Znanie, id=question_pk)

                if QuizResult.objects.filter(user=user, quiz=quiz).exists():
                    old_results = QuizResult.objects.filter(user=user, quiz=quiz)
                    time_now = now()
                    gap_between_possible_results = datetime.timedelta(seconds=20)
                    minimum_time = time_now-gap_between_possible_results
                    if old_results.exclude(date_time__gte=minimum_time).exists():
                        old_results.exclude(date_time__gte=minimum_time).delete()

                QuizResult.objects.create(
                    quiz=quiz,
                    question=question,
                    user=user,
                    answer=answer,
                )

                return JsonResponse({}, status=200)

        raise Http404
