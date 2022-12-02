from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from drevo.models import MaxAgreedQuestion
from drevo.forms.max_agreed_create_form import MaxAgreedQuestionCreateForm
from django.views.generic import CreateView, TemplateView, UpdateView
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect


class MaxAgreedQuestionCreateView(LoginRequiredMixin, CreateView):
    model = MaxAgreedQuestion
    form_class = MaxAgreedQuestionCreateForm
    template_name = 'drevo/max_agreed_question_create.html'
    success_url = reverse_lazy('max_agreed')


    def get(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        return self.render_to_response(self.get_context_data(form=form))

    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            if self.request.user.is_expert:
                max_agreed = MaxAgreedQuestion.objects.create(
                    interview = form.cleaned_data['interview'],
                    question = form.cleaned_data['question'],
                    max_agreed=form.cleaned_data['max_agreed'],
                    author=self.request.user
                )
            return HttpResponseRedirect(reverse('max_agreed',
                    kwargs={'interview_pk':form.cleaned_data['interview'].id,
                    'question_pk':form.cleaned_data['question'].id,
                    'pk':max_agreed.id}))

        return self.form_invalid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))
