from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from drevo.models import Znanie, Relation
from drevo.services import send_notify_interview


def send_notify_view(request, name):
    if request.is_ajax():

        interview = get_object_or_404(Znanie, name=name)
        period_relation = Relation.objects.filter(bz=interview).first().rz.name.split('-')
        # Передаем параметры в функцию send_notify_interview, которая формирует текст сообщения
        result = send_notify_interview(interview, period_relation)
        return JsonResponse({
            'result': result
        })
