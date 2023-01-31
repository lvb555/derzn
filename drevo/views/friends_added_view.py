from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render

from drevo.models.feed_messages import FeedMessage

from ..models import Message
from ..models import FriendsInviteTerm
from users.models import Profile, User

from django.core.exceptions import ObjectDoesNotExist

import math

def friends_added_view(request):
    """
    Контрол страницы "Добавить в друзья"
    """
    context = {'profiles': []}

    # Добавление в друзья
    if request.GET.get('add'):
        _add_friend(request.user.id, request.GET.get('add'))

    # Отмена отправки заявки
    if request.GET.get('cancel'):
        _cancel_invite(request.user.id, request.GET.get('cancel'))

    if request.GET.get('accept'):
        _accept_invite(request.user.id, request.GET.get('accept'))

    # отклонение заявки в друзья
    if request.GET.get('not_accept'):
        _not_accept_invite(request.user.id, request.GET.get('not_accept'))

    # удаление из списка друзей
    if request.GET.get('remove'):
        _remove_friend(request.user.id, request.GET.get('remove'))
        
    profiles_in_page = 3
    current_page = 0

    try:
        current_page = int(request.GET.get('page'))

        if current_page == 0: 
            current_page = 1
    except: 
        current_page = 1

    exclude_ids = [request.user.id]
    profiles = Profile.objects.exclude(id__in=exclude_ids)

    for profile in profiles:
        user = profile.user
        if user.first_name == "" or user.last_name == "":
            exclude_ids.append(profile.id)

    try:
        # Загрузим список заявок на дружбу
        invites = FriendsInviteTerm.objects.filter(recipient = request.user.id)
        invite_count = len(invites)

        context['invites'] = invites
        context['invite_count'] = invite_count if invite_count else 0

        user = User.objects.get(id = request.user.id)

        my_friends = user.user_friends.all() # те, кто в друзьях у меня
        i_in_friends = user.users_friends.all() # те, у кого я в друзьях
        
        all_friends = my_friends.union(i_in_friends, all=False)
        context['friends'] = all_friends

        context['user'] = user
        context['new_knowledge_feed'] = FeedMessage.objects.filter(recipient = user, was_read = False).count()

        context['new_messages'] = Message.objects.filter(recipient = user, was_read = False).count()

        context['new'] = int(context['new_knowledge_feed']) + int(context['invite_count'] + int(context['new_messages'])) 
            
    # ошибка в случае открытия страницы пользователем без аккаунта - обработка ситуации в html-странице 
    except:
        pass

    all_profiles = Profile.objects.exclude(id__in=exclude_ids).order_by('user__last_name').order_by('user__first_name')
    
    profiles = all_profiles[(current_page-1)*profiles_in_page : current_page * profiles_in_page]

    for profile in profiles:
        data = {}

        user = profile.user
        data['first_name'] = user.first_name
        data['last_name'] = user.last_name
        data['avatar'] = profile.avatar or ''
        data['user_id'] = profile.user_id
        data['relation_to_request_user'] = 'no_relation'

        try:
            if FriendsInviteTerm.objects.filter(sender=request.user.id, recipient = profile.user_id).exists():
                data['relation_to_request_user'] = 'subscriber'
            
            elif User.objects.get(id = request.user.id).user_friends.filter(id = int(user.id)).exists() or user.user_friends.filter(id = request.user.id).exists():
                data['relation_to_request_user'] = 'friend'

            elif FriendsInviteTerm.objects.filter(sender=user, recipient = request.user).exists():
                data['relation_to_request_user'] = 'was_invited'

            context['profiles'].append(data)
        except:
            pass

    context['current_page'] = current_page
    context['previous_page'] = current_page - 1
    context['next_page'] = current_page + 1

    all_profiles_count = all_profiles.count()
    context['max_page'] = math.ceil(all_profiles_count / profiles_in_page)

    if current_page == 1:
        context['part_message'] = f'1 - {current_page * len(context["profiles"])} из {all_profiles_count}'
    elif context['next_page'] > context['max_page']:
        context['part_message'] = f'{(current_page - 1) * profiles_in_page + 1}  - {all_profiles_count} из {all_profiles_count}'
    else:
        context['part_message'] = f'{(current_page - 1) * profiles_in_page + 1}  - {current_page * profiles_in_page} из {all_profiles_count}'
    
    template_name = 'drevo/friends_added.html'
    return render(request, template_name, context)


def _add_friend(user_id: int, friend_id: str) -> None:
    """
    Отправить/принять заявку на дружбу
    """
    try:
        term = FriendsInviteTerm.objects.get(sender_id = user_id, recipient_id = int(friend_id))
    except:
        try:
            user_sender = User.objects.get(id = user_id)
            friend = user_sender.user_friends.get(id = int(friend_id))
        except:
            if not user_id == int(friend_id):
                if FriendsInviteTerm.objects.filter(sender_id = int(friend_id), recipient_id = user_id).exists():
                    sent_term = FriendsInviteTerm.objects.get(sender_id = int(friend_id), recipient_id = user_id)
                    sent_term.delete()

                    user_to_add = User.objects.get(id = int(friend_id))
                    user_sender.user_friends.add(user_to_add)
                else:
                    try:
                        user_sender = User.objects.get(id = user_id)
                        friend = User.objects.get(id = int(friend_id))
                        if not friend.user_friends.filter(id = user_sender.id).exists():
                            FriendsInviteTerm.objects.create(sender_id = user_id, recipient_id = int(friend_id))
                    except:
                        pass
            else:
                pass


def _cancel_invite(user_id: int, friend_id: str) -> None:
    """
    Отменить отправленную заявку в друзья
    """
    try:
        term = get_object_or_404(FriendsInviteTerm, sender_id = user_id, recipient_id = int(friend_id))
        term.delete()
    except:
        return JsonResponse({"error": "Такой заявки не было"})


def _remove_friend(user_id: int, friend_id: str) -> None:
    """
    Удалить из друзей
    """
    try:
        user = User.objects.get(id = user_id)
        friend = User.objects.get(id = int(friend_id))

        was_deleted = False

        if user.user_friends.filter(id = friend.id).exists():
            was_deleted = True
            user.user_friends.remove(friend)

        if friend.user_friends.filter(id = user.id).exists():
            was_deleted = True
            friend.user_friends.remove(user)

        if was_deleted:
            msg_text = "Вы удалены из списка моих друзей (сообщение создано автоматически)"
            message = Message.objects.create(sender = user, recipient = friend, text = msg_text, was_read = False)
        
    except ObjectDoesNotExist:
        return JsonResponse({"error": "Такого пользователя в друзьях нет"})


def _accept_invite(user_id: int, friend_id: str) -> None:
    """
    Подтвердить дружбу
    """
    # Удалим из таблицы заявок
    try:
        invite_term = FriendsInviteTerm.objects.filter(recipient_id=user_id, sender_id=int(friend_id))
        if invite_term:
            # Добавим в список друзей (если такая дружба уже есть - ничего не делаем, если нет - создаем)
            user = User.objects.get(id = user_id)
            friend_to_add = User.objects.get(id = int(friend_id))
            if not user.user_friends.filter(id = friend_to_add.id).exists():
                user.user_friends.add(friend_to_add)
        invite_term.delete()
    except:
        return JsonResponse({"error": "Не удалось добавить в друзья"})



def _not_accept_invite(user_id: int, friend_id: str) -> None:
    """
    Отклонить дружбу
    """
    # Удалим из таблицы заявок
    try:
        invite_table = FriendsInviteTerm.objects.get(recipient_id=user_id, sender_id=int(friend_id))
        invite_table.delete()

        user = User.objects.get(id = user_id)
        user_not_accepted = User.objects.get(id = int(friend_id))

        msg_text = "Ваше предложение дружбы отклонено (сообщение создано автоматически)"
        message = Message.objects.create(sender = user, recipient = user_not_accepted, text = msg_text, was_read = False)
    except:
        return JsonResponse({"error": "Заявка была отменена"})