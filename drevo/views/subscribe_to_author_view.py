from django.views.generic import FormView

from drevo.models import Author


class SubscribeToAuthor(FormView):

    template_name = 'drevo/author_subscription.html'

    def get_context_data(self, **kwargs):
        super(SubscribeToAuthor, self).get_context_data(**kwargs)
        subsribed_to = self.request.user.author_set.all()
        # subsribed_to = Author.objects.filter(sub)
        can_subscribe_to = Author.objects.exclude(
            subscribers=self.request.user)
