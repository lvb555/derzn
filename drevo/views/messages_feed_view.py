from django.shortcuts import render

def messages_feed(request):

    template_name = 'drevo/messages_feed.html'
    return render(request, template_name)