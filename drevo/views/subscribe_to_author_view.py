from django.http import HttpResponseRedirect
from django.views.generic import ListView
from drevo.forms import AuthorSubscriptionForm, AuthorSubscriptionDeleteForm
from drevo.models import Author


class SubscribeToAuthor(ListView):
    template_name = 'drevo/author_subscription.html'
    model = Author
    context_object_name = 'subscriptions'
    new_sub_form = AuthorSubscriptionForm

    def get_context_data(self, **kwargs):
        context = super(SubscribeToAuthor, self).get_context_data(**kwargs)
        subsribed_to = self.request.user.author_set.all()
        subsribed_to__names = [(author.name, author.name)
                               for author in subsribed_to]
        can_subscribe_to = Author.objects.exclude(
            subscribers=self.request.user)
        can_subscribe_to__names = [(author.name, author.name) for
                                   author in can_subscribe_to]
        context['new_sub_form'] = AuthorSubscriptionForm(
            subscription_choices=can_subscribe_to__names)
        context['remove_from_sub_form'] = \
            AuthorSubscriptionDeleteForm(
                unsubscribe_choices=subsribed_to__names)
        return context

    def post(self, request, *args, **kwargs):
        if 'btn_sub' in request.POST:
            subscribed_to_names = request.POST.getlist('subscription_choices')
            authors_subscribed_to = Author.objects.filter(
                name__in=subscribed_to_names)
            for author in authors_subscribed_to:
                author.subscribers.add(self.request.user)
        elif 'btn_unsub' in request.POST:
            unsubscribed_from_names = request.POST['unsubscribe_choices']
            authors_subscribed_to = Author.objects.filter(
                name__in=[unsubscribed_from_names])
            for author in authors_subscribed_to:
                author.subscribers.remove(self.request.user)
        return HttpResponseRedirect(self.request.path_info)



    def get_queryset(self):
        """List of subscriptions"""
        return self.request.user.author_set.all()
