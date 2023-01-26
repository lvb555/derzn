from django.http import JsonResponse
from django.shortcuts import render

from drevo.models.feed_messages import FeedMessage
from drevo.models.message import Message
from ..models import FriendsInviteTerm
from users.models import User

from django.core.exceptions import ObjectDoesNotExist


def friends_view(request):
    """
    Контроль для страницы "Друзья"
    """
    context = {'friends': []}

    # принятие заявки в друзья
    if request.GET.get('accept'):
        _accept_invite(request.user.id, request.GET.get('accept'))

    # отклонение заявки в друзья
    if request.GET.get('not_accept'):
        _not_accept_invite(request.user.id, request.GET.get('not_accept'))

    # удаление из списка друзей
    if request.GET.get('remove'):
        _remove_friend(request.user.id, request.GET.get('remove'))

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
        context.update({'friends_count': len(all_friends)})

        context['user'] = user
        context['new_knowledge_feed'] = FeedMessage.objects.filter(recipient = user, was_read = False).count()

        context['new_messages'] = Message.objects.filter(recipient = user, was_read = False).count()

        context['new'] = int(context['new_knowledge_feed']) + int(context['invite_count'] + int(context['new_messages'])) 
            
    # ошибка в случае открытия страницы пользователем без аккаунта - обработка ситуации в html-странице 
    except:
        pass

    template_name = 'drevo/friends.html'
    return render(request, template_name, context)


def _remove_friend(user_id: int, friend_id: str) -> None:
    """
    Удалить из друзей
    """
    try:
        user = User.objects.get(id = user_id)
        friend = User.objects.get(id = int(friend_id))

        if user.user_friends.filter(id = friend.id).exists():
            user.user_friends.remove(friend)

        if friend.user_friends.filter(id = user.id).exists():
            friend.user_friends.remove(user)
        
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
        invite_table = FriendsInviteTerm.objects.filter(recipient_id=user_id, sender_id=int(friend_id))
        invite_table.delete()
    except:
        return JsonResponse({"error": "Заявка была отменена"})