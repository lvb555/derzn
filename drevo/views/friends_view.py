from django.shortcuts import render

from ..models import FriendsTerm
from ..models import FriendsInviteTerm
from users.models import Profile, User


def friends_view(request):
    """
    Контрол для страницы "Друзья"
    """
    context = {'profiles': []}

    # Загрузим список заявок на дружбу
    invite_count = FriendsInviteTerm.objects.filter(recipient=request.user.id).count()
    context['invite_count'] = invite_count if invite_count else 0

    # Удаление из списка друзей
    if request.GET.get('remove'):
        _remove_friend(request.user.id, request.GET.get('remove'))

    user_obj = FriendsTerm.objects.filter(user_id=request.user.id).first()
    if user_obj:
        profiles = Profile.objects.filter(id=user_obj.friend_id)
        for profile in profiles:
            data = {}
            user = User.objects.filter(id=profile.user_id).first()
            if not user:
                continue
            if not user.first_name or not user.last_name:
                continue
            data['first_name'] = user.first_name
            data['last_name'] = user.last_name
            data['avatar'] = profile.avatar or ''
            data['user_id'] = profile.user_id
            context['profiles'].append(data)

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
