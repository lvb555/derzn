from django.shortcuts import redirect, render
from django.urls import reverse
from drevo.forms.send_to_feed_form import SendToFeedForm
from drevo.models.feed_messages import FeedMessage, LabelFeedMessage
from drevo.models.friends import FriendsTerm
from drevo.models.knowledge import Znanie
from users.models import Profile, User


def send_to_feed_view(request, znanie_id: int):
    """
    Логика для страницы отправки сообщения
    """
    context = {'znanie': 0, 'labels': 0, 'friends': []}

    znanie = Znanie.objects.get(id = znanie_id)
    context['znanie'] = znanie

    labels = LabelFeedMessage.objects.all()
    context['labels'] = labels

    # создание списка для отображения в блоке отправления
    user_friendships = FriendsTerm.objects.filter(user_id=request.user)
    for friend_link in user_friendships:
        data = {}
        data['user'] = friend_link.friend
        data['profile'] = Profile.objects.get(user_id = friend_link.friend)
        context['friends'].append(data)

    # если был получен ajax-запрос
    if request.method == 'POST':

        msg_text = request.POST.get('text')
        msg_label = request.POST.get('label_id')
        send_to = list(request.POST.getlist('send_to_ids[]'))
        
        for user_in_array in send_to:
            if user_in_array != request.user:
                try:
                    user_recipient = User.objects.get(id = int(user_in_array))
                    msg_label_new = LabelFeedMessage.objects.get(id = int(msg_label))
                    msg_znanie = Znanie.objects.get(id = znanie_id)

                    new_msg = FeedMessage.objects.create(sender = request.user, recipient = user_recipient, label = msg_label_new, znanie = msg_znanie,
                    text = msg_text, was_read = False)
                    new_msg.save()
                except Exception:
                    pass

    template_name = 'drevo/send_to_feed.html'
    return render(request, template_name, context)