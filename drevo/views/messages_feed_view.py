from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from drevo.models.feed_messages import FeedMessage
from drevo.models.friends_invite import FriendsInviteTerm

from drevo.models.message import Message

from django.core.exceptions import BadRequest

from users.models import User
from users.views import access_sections


def messages_feed(request):
    context = {}

    try:
        messages = Message.objects.filter(recipient = request.user).order_by('-id')
        unread_count = 0

        for message in messages:
            if not message.was_read:
                unread_count += 1

        context.update({"messages": messages, "unread_count": unread_count})

        # Загрузим список заявок на дружбу
        invites = FriendsInviteTerm.objects.filter(recipient = request.user.id)
        invite_count = len(invites)

        context['invites'] = invites
        context['invite_count'] = invite_count if invite_count else 0

        user = User.objects.get(id = request.user.id)
        context['sections'] = access_sections(user)
        context['activity'] = [i for i in context['sections'] if i.startswith('Мои') or
                               i.startswith('Моя')]
        context['link'] = 'users:myprofile'
        my_friends = user.user_friends.all() # те, кто в друзьях у меня
        i_in_friends = user.users_friends.all() # те, у кого я в друзьях
        
        all_friends = my_friends.union(i_in_friends, all=False)
        context['friends'] = all_friends

        context['user'] = user
        context['new_knowledge_feed'] = FeedMessage.objects.filter(recipient = user, was_read = False).count()

        context['new'] = int(context['new_knowledge_feed']) + int(context['invite_count'] + int(context['unread_count'])) 
            
    # ошибка в случае открытия страницы пользователем без аккаунта - обработка ситуации в html-странице 
    except:
        pass
    if request.method == 'POST':
        task = request.POST.get('task')
        if task == "read_message":
            try:
                message_id = request.POST.get('message_id')
                message_in_feed = get_object_or_404(Message, id = message_id)

                if message_in_feed.was_read == True:
                    message_in_feed.was_read = False

                else:
                    message_in_feed.was_read = True
                
                message_in_feed.save()
                    
                return JsonResponse({"done": True})

            except Message.DoesNotExist: # сообщение не найдено
                response = JsonResponse({"error": "Сообщение не найдено!", "done": False})
                response.status_code = 404
                return response

            except BadRequest: # ошибка с данными в запросе
                response = JsonResponse({"error": "Ошибка в запросе!", "done": False})
                response.status_code = 400
                return response

    template_name = 'drevo/messages_feed.html'
    return render(request, template_name, context)