from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render

from drevo.models.message import Message
from users.models import User

def send_message(request):

    if request.method == "POST":
        task = request.POST.get('task')

        if task == "send_message":
            # данные из ajax-запроса
            msg_text = request.POST.get('text')
            send_to = list(request.POST.getlist('send_to_ids[]'))

            users_to_send = User.objects.filter(id__in = send_to).exclude(id = request.user.id)

            try:
                messages_to_send = []
                
                for user_to_send in users_to_send:
                    messages_to_send.append(Message(sender = request.user, recipient = user_to_send, text = msg_text, was_read = False))

                messages_sent = Message.objects.bulk_create(messages_to_send)

                return JsonResponse({"done": True})
                    
            except Exception:
                return JsonResponse({"error": "Не получилось отправить сообщение!"})


def delete_message(request, message_id):
    """
    Логика удаления сообщения
    """
    try:
        message = Message.objects.get(id = message_id)
        message.delete()
    except:
        pass

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))