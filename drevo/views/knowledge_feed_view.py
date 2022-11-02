from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from drevo.models.feed_messages import FeedMessage
from users.models import Profile


def knowledge_feed_view(request):
    """
    Контроль для страницы "Лента знаний"
    """
   
    context = {'messages': [], 'unread': 0}

    messages = FeedMessage.objects.filter(recipient = request.user).order_by('-id')
    for message in messages:
        data = {}
        data['message'] = message
        profile = Profile.objects.get(user_id = message.sender.id)
        data['znanie'] = message.znanie
        data['sender'] = profile
        context['messages'].append(data)

    context['unread'] = FeedMessage.objects.filter(recipient = request.user, was_read=False).count()

    if request.method == 'POST':   
        try:
            message_id = request.POST.get('checkbox')
            message_in_feed = FeedMessage.objects.get(id = message_id)
            if message_in_feed.was_read == True:
                message_in_feed.was_read = False
                message_in_feed.save()

            else:
                message_in_feed.was_read = True
                message_in_feed.save()
        except:
            pass

    template_name = 'drevo/knowledge_feed.html'

    return render(request, template_name, context)

def delete_message(request, message_id):
    """
    Логика удаления сообщения
    """
    message = FeedMessage.objects.get(id = message_id)
    message.delete()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))