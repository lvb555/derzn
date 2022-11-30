from django.views.generic import ListView
from drevo.models import MaxAgreedQuestion


class MaxAgreedQuestionListView(ListView):
    """
    выводит список максимальных согласий с ответами на вопросы эксперта
    """

    template_name = "drevo/max_agreed_list_view.html"
    model = MaxAgreedQuestion
    context_object_name = "all_max_agreed"

    def get_queryset(self):
        user = self.request.user
        return MaxAgreedQuestion.objects.filter(author_id=user)
