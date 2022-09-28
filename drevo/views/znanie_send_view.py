from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, redirect
from django.urls import reverse_lazy

from ..forms.znanie_send_message_form import ZnanieSendMessage
from ..models.knowledge import Znanie
from ..sender import send_email


@login_required
def send_znanie(request, pk):
    znanie = Znanie.objects.values('name', 'is_send').get(pk=pk)
    if not znanie.get('is_send'):
        raise Http404
    if request.method == 'POST':
        form = ZnanieSendMessage(request.POST)
        if form.is_valid():
            address = form.cleaned_data['email_address']
            znanie_url = f"{settings.BASE_URL}{reverse_lazy('zdetail', kwargs={'pk': pk})}"
            message_subject = 'Интересная информация на портале "Дерево знаний'
            message_text = form.cleaned_data['mes_text'] + f"\n {znanie_url}"
            is_send = send_email(to_address=address, subject=message_subject, message=message_text, html_message=False)
            if is_send:
                return redirect('zdetail', pk=pk)
            else:
                messages.error(request, 'При отправке произошла ошибка, попробуйте позже.')
    else:
        form = ZnanieSendMessage()
    return render(request, 'drevo/znanie_send_message.html', {'form': form, 'znanie_name': znanie})
