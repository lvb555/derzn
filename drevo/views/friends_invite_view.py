from django.shortcuts import render

from ..models import FriendsInviteTerm
from ..models import FriendsTerm
from users.models import Profile, User


def friends_invite_view(request):
    """
    Контрол для страницы "Заявки в друзья"
    """
    context = {'profiles': []}

    # Обработать поведени "Принять" или "Отклонить заявку"
    if request.GET.get('accept'):
        _accept_invite(request.user.id, request.GET.get('accept'))

    if request.GET.get('not_accept'):
        _not_accept_invite(request.user.id, request.GET.get('not_accept'))

    array_invite = []
    invite_friend = FriendsInviteTerm.objects.filter(recipient_id=request.user.id)
    for one in invite_friend:
        array_invite.append(one.sender_id)
    profiles = Profile.objects.filter(user_id__in=array_invite)
    for profile in profiles:
        data = {}
        user = User.objects.filter(id=profile.user_id)
        if not user.exists():
            continue
        if not user[0].first_name and not user[0].last_name:
            continue
        data['first_name'] = user[0].first_name
        data['last_name'] = user[0].last_name
        data['avatar'] = profile.avatar
        data['user_id'] = profile.user_id
        context['profiles'].append(data)

    template_name = 'drevo/friends_invite.html'
    return render(request, template_name, context)


def _accept_invite(user_id: int, friend_id: str) -> None:
    """
    Подтвердить дружбу
    """
    # Удалим из таблицы заявок
    invite_table = FriendsInviteTerm.objects.filter(recipient_id=user_id, sender_id=int(friend_id))
    invite_table.delete()

    # Добавим в список друзей
    FriendsTerm.objects.create(
        user_id=user_id,
        friend_id=friend_id
    )
    FriendsTerm.objects.create(
        user_id=friend_id,
        friend_id=user_id
    )


def _not_accept_invite(user_id: int, friend_id: str) -> None:
    """
    Отклонить дружбу
    """
    # Удалим из таблицы заявок
    invite_table = FriendsInviteTerm.objects.filter(recipient_id=user_id, sender_id=int(friend_id))
    invite_table.delete()
