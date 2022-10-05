from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse_lazy

from ..forms.znanie_send_message_form import ZnanieSendMessage
from ..models.knowledge import Znanie
from ..sender import send_email


@login_required
def send_znanie(request, pk):
    znanie = Znanie.objects.values('pk', 'name', 'is_send').get(pk=pk)
    if not znanie.get('is_send'):
        raise Http404
    if request.method == 'POST':
        form = ZnanieSendMessage(request.POST)
        if form.is_valid():
            address = form.cleaned_data['email_address']
            znanie_url = f"{settings.BASE_URL}{reverse_lazy('zdetail', kwargs={'pk': pk})}"
            message_subject = 'Интересная информация на портале "Дерево знаний"'
            context = dict(
                mes_text=form.cleaned_data['mes_text'],
                url=znanie_url,
                znanie_name=znanie.get('name'),
                user_name=request.user.get_full_name()
            )
            message_html = render_to_string('knowledge_send_email.html', context)
            is_send = send_email(address, message_subject, message_html, message_html)
            if is_send:
                context = {'form': ZnanieSendMessage(), 'znanie_name': znanie, 'is_send': is_send}
                return render(request, 'drevo/znanie_send_message.html', context)
            else:
                messages.error(request, 'При отправке произошла ошибка, попробуйте позже.')
    else:
        form = ZnanieSendMessage()
    return render(request, 'drevo/znanie_send_message.html', {'form': form, 'znanie_name': znanie})
