from django.views.generic import TemplateView
from drevo.models import MaxAgreedQuestion
from django.db.models import Q


class MaxAgreedQuestionView(TemplateView):
    """
    Максимальное число согласий с ответами на вопрос
    """

    template_name = "drevo/max_agreed_question.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        max_agreed = MaxAgreedQuestion.objects.get(id=self.kwargs["pk"])
        context["max_agreed"] = max_agreed

        return context
