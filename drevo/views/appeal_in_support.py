from datetime import datetime
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from drevo.forms.appeal import TicketForm
from drevo.models.appeal import Appeal
from users.models import User


@login_required
def appeal(request):
    if request.user.is_staff:
        answered_tickets = Appeal.objects.filter(resolved=True).order_by('-created_at')
        unanswered_tickets = Appeal.objects.filter(resolved=False).order_by('-created_at')
        users = User.objects.all()
        if request.is_ajax():
            ticket_id = request.GET.get('ticket_id')
            message = request.GET.get('message')
            ticket = Appeal.objects.get(id=int(ticket_id))
            ticket.message = message
            ticket.admin = request.user
            ticket.resolved = True
            ticket.answered_at = datetime.now()
            ticket.save()
            return JsonResponse({'status': 'success'})
        return render(request, 'drevo/admin_appeal.html', {'answered_tickets': answered_tickets, 'users': users,
                                                           'unanswered_tickets': unanswered_tickets})
    else:
        answered_tickets = Appeal.objects.filter(user=request.user, resolved=True).order_by('-created_at')
        unanswered_tickets = Appeal.objects.filter(user=request.user, resolved=False).order_by('-created_at')
        if request.method == 'POST':
            form = TicketForm(request.POST)
            if form.is_valid():
                subject = form.cleaned_data['subject']
                description = form.cleaned_data['description']
                Appeal.objects.create(user=request.user, subject=subject, description=description)
                return redirect('appeal')
        else:
            form = TicketForm()
        return render(request, 'drevo/user_appeal.html', {'answered_tickets': answered_tickets,
                                                           'unanswered_tickets': unanswered_tickets, 'form': form})
