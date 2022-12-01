from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from drevo.models.feed_messages import FeedMessage
from django.core.exceptions import BadRequest
from drevo.models.knowledge import Znanie

from drevo.models.label_feed_message import LabelFeedMessage
from users.models import User


def knowledge_feed_view(request):
    """
    Контроль для страницы "Лента знаний";
    Направляет на страницу "Лента знаний", выводя все сообщения пользователя по новизне
    и показывая число непрочитанных сообщений;
    В ней же обрабатывается ajax-апрос на "прочтение" каждого отдельного сообщения 
    """
   
    context = {'messages': [], 'unread': 0, 'labels': [], 'friends': [], 'friends_count': 0}

    try:
        messages = FeedMessage.objects.filter(recipient = request.user).order_by('-id').prefetch_related("sender__profile")
        context['messages'] = messages

        unread = 0
        for message in messages:
            if message.was_read == False:
                unread += 1

        context['unread'] = unread
        
    # ошибка в случае открытия страницы пользователем без аккаунта - обработка ситуации в html-странице 
    except TypeError:
        pass

    labels = LabelFeedMessage.objects.all()
    context['labels'] = labels

    # создание списка для отображения в блоке отправления
    try:
        user = User.objects.get(id = request.user.id)
        my_friends = user.user_friends.all().prefetch_related('profile') # те, кто в друзьях у меня
        i_in_friends = user.users_friends.all().prefetch_related('profile') # те, у кого я в друзьях
        
        all_friends = my_friends.union(i_in_friends, all=False)

        # user_friendships = FriendsTerm.objects.filter(user_id=request.user).prefetch_related('friend__profile')
        context['friends'] = all_friends
        context['friends_count'] = len(all_friends)
    
    # ошибка в случае открытия страницы пользователем без аккаунта - обработка ситуации в html-странице 
    except TypeError:
        pass


    if request.method == 'POST':
        task = request.POST.get('task')
        if task == "read_message":
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

        elif task == "send_message":
            # данные из ajax-запроса
            msg_text = request.POST.get('text')
            msg_label = request.POST.get('label_id')
            send_to = list(request.POST.getlist('send_to_ids[]'))
            znanie_name = request.POST.get('znanie_name')

            users_to_send = User.objects.filter(id__in=send_to).exclude(id=request.user.id)

            try:
                messages_to_send = []

                # ярлык и знание сообщения
                msg_label_new = LabelFeedMessage.objects.get(id = int(msg_label))
                msg_znanie = Znanie.objects.get(name = znanie_name)

                try:
                    for user_to_send in users_to_send:
                        messages_to_send.append(FeedMessage(sender = request.user, recipient = user_to_send, label = msg_label_new, znanie = msg_znanie,
                        text = msg_text, was_read = False))

                    messages_sent = FeedMessage.objects.bulk_create(messages_to_send)

                    return JsonResponse({"done": True})
                    
                except Exception:
                    return JsonResponse({"error": "Не получилось отправить сообщение!"})

            except TypeError: # ошибка возникает с типом данных msg_label, при этом ни на что не влияет и сообщение в базе создается
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