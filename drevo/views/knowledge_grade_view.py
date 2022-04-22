from django.views.generic import FormView
from drevo.forms.knowledge_grade_form import KnowledgeGradeForm
from drevo.models.knowledge_grade import KnowledgeGrade
from drevo.models.knowledge import Znanie
from users.models import User


class KnowledgeFormView(FormView):
    form_class = KnowledgeGradeForm
    template_name = 'drevo/knowledge_grade.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Оценка знания'
        # print(context)
        return context

    def get_success_url(self):
        return self.request.path

    def get_form(self, form_class=None):
        kwargs = self.get_form_kwargs()
        if self.request.method == 'GET':
            kwargs['initial']['user'] = self.request.user.id
            kwargs['initial']['knowledge'] = self.kwargs.get('pk')
        return self.form_class(**kwargs)

    def post(self, request, *args, **kwargs):
        return super(KnowledgeFormView, self).post(request, *args, **kwargs)
