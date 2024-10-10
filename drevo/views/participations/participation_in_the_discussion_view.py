from django.views.generic import DetailView

from drevo.models import Znanie
from drevo.relations_tree import get_descendants_for_knowledge


class ParticipationInTheDiscussionView(DetailView):
    template_name = "drevo/participation_in_the_discussion.html"
    model = Znanie
    context_object_name = "znanie"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.object.pk
        knowledge = Znanie.objects.get(pk=pk)
        context['relative_znania'] = get_descendants_for_knowledge(knowledge)

        return context
