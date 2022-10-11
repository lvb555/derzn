from django.db.models import Q
from django.http import Http404
from django.views.generic import ListView, DetailView
from ...models import Relation
from ...models.interview_answer_expert_proposal import InterviewAnswerExpertProposal
from ...models.knowledge import Znanie


def chek_is_stuff(user) -> None:
    if not user.is_staff:
        raise Http404
    return None


class AllInterviewView(ListView):
    """
        Выводит список всех интервью
    """
    template_name = 'drevo/admin_interview_work_page/interviews_list.html'

    def dispatch(self, request, *args, **kwargs):
        chek_is_stuff(request.user)
        return super(AllInterviewView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Znanie.objects.select_related('tz', 'category').filter(tz__name='Интервью').all()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(AllInterviewView, self).get_context_data(**kwargs)
        data = {elm.category.name: [] for elm in self.object_list}

        for elm in self.object_list:
            category = elm.category.name
            title = elm.name
            questions = Relation.objects.select_related('rz').prefetch_related('rz__tz').filter(
                Q(bz__pk=elm.pk) & Q(rz__tz__name='Вопрос')
            ).values('rz')
            q_count = questions.count()
            status = 'success'
            for quest in questions:
                exp_prop = InterviewAnswerExpertProposal.objects.filter(
                    Q(question__pk=quest.get('rz')) & Q(status=None)
                )
                if exp_prop.exists():
                    status = 'danger'
                    break
            data[category].append((elm.pk, title, q_count, status))

        context['data'] = data
        return context


class InterviewQuestionsView(DetailView):
    """
        Выводит список вопросов интервью
    """
    model = Znanie
    template_name = 'drevo/admin_interview_work_page/interview_questions.html'
    context_object_name = 'interview'

    def dispatch(self, request, *args, **kwargs):
        chek_is_stuff(request.user)
        return super(InterviewQuestionsView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(InterviewQuestionsView, self).get_context_data(**kwargs)
        questions = Relation.objects.prefetch_related('rz__tz').filter(
            Q(bz=self.object) & Q(rz__tz__name='Вопрос')
        ).values('rz', 'rz__name')

        data = []

        for quest in questions:
            status = 'success'
            danger_cnt = None
            exp_prop = InterviewAnswerExpertProposal.objects.filter(Q(question__pk=quest.get('rz')) & Q(status=None))
            if exp_prop.exists():
                status = 'danger'
                danger_cnt = exp_prop.count()
            data.append((quest.get('rz'), quest.get('rz__name'), danger_cnt, status))
        context['interview_pk'] = self.object.pk
        context['questions'] = data
        return context


class QuestionAdminWorkView(ListView):
    """
        Выводит таблицу с данными о всех предложениях экспертов интервью
    """
    model = InterviewAnswerExpertProposal
    template_name = 'drevo/admin_interview_work_page/question_admin_work.html'
    context_object_name = 'questions'

    def dispatch(self, request, *args, **kwargs):
        chek_is_stuff(request.user)
        return super(QuestionAdminWorkView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return InterviewAnswerExpertProposal.objects.filter(
            question__pk=self.kwargs['quest_pk'], interview__pk=self.kwargs['inter_pk']
        )

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(QuestionAdminWorkView, self).get_context_data(**kwargs)

        interview = Znanie.objects.values('pk', 'name').get(pk=self.kwargs['inter_pk'])
        context['interview_name'] = interview.get('name')
        period = Relation.objects.select_related('tr', 'rz').filter(
            Q(bz__pk=interview.get('pk')) & Q(tr__name='Период интервью')
        ).first().rz.name

        question = Znanie.objects.values('name').get(pk=self.kwargs['quest_pk'])
        context['question_name'] = question.get('name')
        context['period'] = f"с {period}".replace('-', 'по')
        return context
