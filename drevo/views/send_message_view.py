from django.http import HttpResponseRedirect
from django.shortcuts import render

from drevo.models.message import Message

def send_message(request, id):

    template_name = 'drevo/send_message.html'
    return render(request, template_name)


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