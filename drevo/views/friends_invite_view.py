from django.http import JsonResponse
from django.shortcuts import render

from users.models import User

from ..models import FriendsInviteTerm


def friends_invite_view(request):
    """
    Контрол для страницы "Заявки в друзья"
    """
    context = {'profiles': []}

    # Обработать поведение "Принять" или "Отклонить заявку"
    if request.GET.get('accept'):
        _accept_invite(request.user.id, request.GET.get('accept'))

    if request.GET.get('not_accept'):
        _not_accept_invite(request.user.id, request.GET.get('not_accept'))



    user_friends_invites = FriendsInviteTerm.objects.filter(recipient_id=request.user)
    for friend_link in user_friends_invites:
        user = friend_link.sender
        context['profiles'].append(user)

    template_name = 'drevo/friends_invite.html'
    return render(request, template_name, context)


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
            # first_friendship = FriendsTerm.objects.get_or_create(user_id=user_id, friend_id=friend_id)
            # second_friendship = FriendsTerm.objects.get_or_create(user_id=friend_id, friend_id=user_id)
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
