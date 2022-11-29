from django.http import JsonResponse
from django.shortcuts import render

from ..models import FriendsInviteTerm
from users.models import User

from django.core.exceptions import ObjectDoesNotExist


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

    try:
        user = User.objects.get(id = request.user.id)

        my_friends = user.user_friends.all() # те, кто в друзьях у меня
        i_in_friends = user.users_friends.all() # те, у кого я в друзьях
        
        all_friends = my_friends.union(i_in_friends, all=False)
        context['friends'] = all_friends
            
    # ошибка в случае открытия страницы пользователем без аккаунта - обработка ситуации в html-странице 
    except TypeError:
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
