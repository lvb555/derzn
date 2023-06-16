from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from drevo.models.feed_messages import FeedMessage
from django.core.exceptions import BadRequest
from drevo.models.friends_invite import FriendsInviteTerm
from drevo.models.knowledge import Znanie

from drevo.models.label_feed_message import LabelFeedMessage
from drevo.models.message import Message
from users.models import User

import math

from users.views import access_sections


def knowledge_feed_view(request):
    """
    Контроль для страницы "Лента знаний";
    Направляет на страницу "Лента знаний", выводя все сообщения пользователя по новизне
    и показывая число непрочитанных сообщений;
    В ней же обрабатывается ajax-апрос на "прочтение" каждого отдельного сообщения 
    """
   
    context = {'messages': [], 'unread': 0, 'labels': [], 'friends': [], 'friends_count': 0}

    try:
        messages_in_page = 4

        try:
            current_page = int(request.GET.get('page'))

            if current_page == 0: 
                current_page = 1
        except: 
            current_page = 1

        user = User.objects.get(id = request.user.id)
        context['sections'] = access_sections(user)
        context['activity'] = [i for i in context['sections'] if i.startswith('Мои') or
                               i.startswith('Моя')]
        context['link'] = 'users:myprofile'

        messages = FeedMessage.objects.filter(recipient = request.user).order_by('-id').prefetch_related("sender__profile")[(current_page-1)*messages_in_page : current_page * messages_in_page]
        context['messages'] = messages

        context['current_page'] = current_page
        context['previous_page'] = current_page - 1
        context['next_page'] = current_page + 1

        all_messages = FeedMessage.objects.filter(recipient = request.user).count()
        context['max_page'] = math.ceil(all_messages / messages_in_page)

        if current_page == 1:
            context['part_message'] = f'1 - {current_page * messages_in_page} из {all_messages}'
        elif context['next_page'] > context['max_page']:
            context['part_message'] = f'{(current_page - 1) * messages_in_page + 1}  - {all_messages} из {all_messages}'
        else:
            context['part_message'] = f'{(current_page - 1) * messages_in_page + 1}  - {current_page * messages_in_page} из {all_messages}'

        unread = 0
        for message in FeedMessage.objects.filter(recipient = request.user):
            if message.was_read == False:
                unread += 1

        context['unread'] = unread

        invites = FriendsInviteTerm.objects.filter(recipient = request.user.id)
        invite_count = len(invites)

        context['invites'] = invites
        context['invite_count'] = invite_count if invite_count else 0

        context['user'] = request.user
        # context['new_knowledge_feed'] = FeedMessage.objects.filter(recipient = request.user, was_read = False).count()

        context['new_messages'] = Message.objects.filter(recipient = request.user, was_read = False).count()

        context['new'] = int(context['unread']) + int(context['invite_count'] + int(context['new_messages']))
        
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

        context['friends'] = all_friends
        context['friends_count'] = len(all_friends)
    
    # ошибка в случае открытия страницы пользователем без аккаунта - обработка ситуации в html-странице 
    except:
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