from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

from ..models import FriendsInviteTerm
from users.models import Profile, User


def friends_added_view(request):
    """
    Контрол страницы "Добавить в друзья"
    """
    context = {'profiles': []}
    first_name_predicate = request.GET.get('first')
    last_name_predicate = request.GET.get('last')

    # Добавление в друзья
    if request.GET.get('add'):
        _add_friend(request.user.id, request.GET.get('add'))

    # Отмена отправки заявки
    if request.GET.get('cancel'):
        _cancel_invite(request.user.id, request.GET.get('cancel'))

    exclude_ids = [request.user.id]
    profiles = Profile.objects.exclude(id__in=exclude_ids)
    for profile in profiles:
        data = {}
        if first_name_predicate and not last_name_predicate:
            user = User.objects.filter(id=profile.user_id, first_name__contains=first_name_predicate).first()
        elif not first_name_predicate and last_name_predicate:
            user = User.objects.filter(id=profile.user_id, last_name__contains=last_name_predicate).first()
        elif first_name_predicate and last_name_predicate:
            user = User.objects.filter(id=profile.user_id, first_name__contains=first_name_predicate,
                                       last_name__contains=last_name_predicate).first()
        else:
            user = User.objects.filter(id=profile.user_id).first()
        if not user:
            continue
        if not user.first_name or not user.last_name:
            continue

        data['first_name'] = user.first_name
        data['last_name'] = user.last_name
        data['avatar'] = profile.avatar or ''
        data['user_id'] = profile.user_id
        data['relation_to_request_user'] = 'no_relation'
    
        if FriendsInviteTerm.objects.filter(sender=request.user.id, recipient = profile.user_id).exists():
            data['relation_to_request_user'] = 'subscriber'
        
        elif User.objects.get(id = request.user.id).user_friends.filter(id = int(user.id)).exists() or user.user_friends.filter(id = request.user.id).exists():
            data['relation_to_request_user'] = 'friend'

        elif FriendsInviteTerm.objects.filter(sender=user, recipient = request.user).exists():
            data['relation_to_request_user'] = 'was_invited'

        context['profiles'].append(data)

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