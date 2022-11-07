from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from drevo.models.feed_messages import FeedMessage
from django.core.exceptions import BadRequest


def knowledge_feed_view(request):
    """
    Контроль для страницы "Лента знаний";
    Направляет на страницу "Лента знаний", выводя все сообщения пользователя по новизне
    и показывая число непрочитанных сообщений;
    В ней же обрабатывается ajax-апрос на "прочтение" каждого отдельного сообщения 
    """
   
    context = {'messages': [], 'unread': 0}

    messages = FeedMessage.objects.filter(recipient = request.user).order_by('-id').prefetch_related("sender__profile")
    context['messages'] = messages

    unread = 0
    for message in messages:
        if message.was_read == False:
            unread += 1

    context['unread'] = unread

    if request.method == 'POST':   
        try:
            message_id = request.POST.get('message_id')
            message_in_feed = get_object_or_404(FeedMessage, id = message_id)
            if message_in_feed.was_read == True:
                message_in_feed.was_read = False
                message_in_feed.save()

            else:
                message_in_feed.was_read = True
                message_in_feed.save()
                
            return JsonResponse({"done": True})

        except FeedMessage.DoesNotExist: # сообщение не найдено
            response = JsonResponse({"error": "Сообщение не найдено!", "done": False})
            response.status_code = 404
            return response

        except BadRequest: # ошибка с данными в запросе
            response = JsonResponse({"error": "Ошибка в запросе!", "done": False})
            response.status_code = 400
            return response


    template_name = 'drevo/knowledge_feed.html'

    return render(request, template_name, context)


def delete_message(request, message_id):
    """
    Логика удаления сообщения
    """
    message = FeedMessage.objects.get(id = message_id)
    message.delete()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))