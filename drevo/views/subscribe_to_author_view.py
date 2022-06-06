from django.http import HttpResponseRedirect
from django.views import View
from django.views.generic import FormView, ListView, TemplateView, UpdateView

from drevo.models import Author

from drevo.forms import AuthorSubscriptionForm, AuthorSubscriptionDeleteForm


class SubscribeToAuthor(ListView,#  UpdateView FormView
                        ):
    template_name = 'drevo/author_subscription.html'
    model = Author
    context_object_name = 'subscriptions'
    new_sub_form = AuthorSubscriptionForm
    # unsub_form = AuthorSubscriptionDeleteForm
    # success_url = 'subscribe_to_author'


    # form_class = AuthorSubscriptionForm

    def get_context_data(self, **kwargs):
        context = super(SubscribeToAuthor, self).get_context_data(**kwargs)
        subsribed_to = self.request.user.author_set.all()
        subsribed_to__names = [(author.name, author.name)
                               for author in subsribed_to]
        # subsribed_to = Author.objects.filter(sub)
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
            print(subscribed_to_names)
            authors_subscribed_to = Author.objects.filter(
                name__in=subscribed_to_names)
            print('--------')
            print(authors_subscribed_to)
            print('--------')
            for author in authors_subscribed_to:
                print(author)
                author.subscribers.add(self.request.user)

            # post_data = request.POST or None
            # sub_form = self.new_sub_form(post_data)
            print(request.POST)
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
