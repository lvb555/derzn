from django.views.generic.edit import DeleteView
from django.urls import reverse_lazy,reverse
from drevo.models import MaxAgreedQuestion
from django.shortcuts import redirect
from django.http import HttpResponseRedirect

class MaxAgreedQuestionDeleteView(DeleteView):
    """
    Удаляет (максимальное число) согласий эксперта с ответами на вопрос интервью
    """

    model = MaxAgreedQuestion
    success_url = reverse_lazy(
        "max_agreed_list"
    )
