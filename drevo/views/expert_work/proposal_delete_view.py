from django.views.generic.edit import DeleteView
from django.urls import reverse_lazy
from django.shortcuts import redirect
from drevo.models import InterviewAnswerExpertProposal
from django.http import HttpResponseRedirect


class ProposalDeleteView(DeleteView):
    """
    Удаляет мнение эксперта по ответу на вопрос интервью
    """

    model = InterviewAnswerExpertProposal

    def get_success_url(self):
        return self.request.META.get('HTTP_REFERER')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        return redirect(success_url,args=(self.request.POST.get('interview_pk'),
        self.request.POST.get('question_pk'),))
