from django.http import JsonResponse
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
    context = {'znanie': 0, 'labels': 0, 'friendships': []}

    znanie = Znanie.objects.get(id = znanie_id)
    context['znanie'] = znanie

    labels = LabelFeedMessage.objects.all()
    context['labels'] = labels

    # создание списка для отображения в блоке отправления
    user_friendships = FriendsTerm.objects.filter(user_id=request.user).prefetch_related('friend__profile')
    context['friendships'] = user_friendships

    # если был получен ajax-запрос
    if request.method == 'POST':

        # данные из ajax-запроса
        msg_text = request.POST.get('text')
        msg_label = request.POST.get('label_id')
        send_to = list(request.POST.getlist('send_to_ids[]'))

        users_to_send = User.objects.filter(id__in=send_to).exclude(id=request.user.id)

        try:
            messages_to_send = []

            # ярлык и знание сообщения
            msg_label_new = LabelFeedMessage.objects.get(id = int(msg_label))
            msg_znanie = Znanie.objects.get(id = znanie_id)

            try:
                for user_to_send in users_to_send:
                    messages_to_send.append(FeedMessage(sender = request.user, recipient = user_to_send, label = msg_label_new, znanie = msg_znanie,
                    text = msg_text, was_read = False))

                messages_sent = FeedMessage.objects.bulk_create(messages_to_send)
            except Exception:
                return JsonResponse({"error": "Не получилось отправить сообщение!"})

        except TypeError: # ошибка возникает с типом данных msg_label, при этом ни на что не влияет и сообщение в базе создается
            pass

    template_name = 'drevo/send_to_feed.html'
    return render(request, template_name, context)