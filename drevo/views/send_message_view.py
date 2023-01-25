from django.shortcuts import render

def send_message(request, id):

    template_name = 'drevo/send_message.html'
    return render(request, template_name)