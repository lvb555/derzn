from django.shortcuts import render

from ..models import FriendsTerm
from ..models import FriendsInviteTerm
from users.models import Profile, User


def friends_view(request):
    """
    Контроль для страницы "Друзья"
    """
    context = {'friends': []}

    # Загрузим список заявок на дружбу
    invite_count = FriendsInviteTerm.objects.filter(recipient=request.user.id).count()
    context['invite_count'] = invite_count if invite_count else 0

    # Удаление из списка друзей
    if request.GET.get('remove'):
        _remove_friend(request.user.id, request.GET.get('remove'))

    user_friend_links = FriendsTerm.objects.filter(user=request.user).prefetch_related("friend")
    for friend_link in user_friend_links:
        data = {}

        user = friend_link.friend
        profile = Profile.objects.get(user_id = user)

        data['first_name'] = user.first_name
        data['last_name'] = user.last_name
        data['avatar'] = profile.avatar or ''
        data['user_id'] = user.id
        context['friends'].append(data)

    template_name = 'drevo/friends.html'
    return render(request, template_name, context)


def _remove_friend(user_id: int, friend_id: str) -> None:
    """
    Удалить из друзей
    """
    friend_table = FriendsTerm.objects.filter(user_id=user_id, friend_id=int(friend_id))
    friend_table.delete()

    friend_table = FriendsTerm.objects.filter(user_id=int(friend_id), friend_id=user_id)
    friend_table.delete()
