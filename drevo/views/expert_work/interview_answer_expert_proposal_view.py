from django.views.generic.detail import DetailView
from django.urls import reverse_lazy
from drevo.models import InterviewAnswerExpertProposal


class InterviewAnswerExpertProposalView(DetailView):
    """
    Отображение мнения эксперта по ответу на вопрос интервью
    """

    model = InterviewAnswerExpertProposal
    success_url = reverse_lazy("/drevo/")
