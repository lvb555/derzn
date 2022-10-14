from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.forms import modelformset_factory
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView
from ...models import Relation, Tz, Author, Tr
from ...models.interview_answer_expert_proposal import InterviewAnswerExpertProposal
from ...models.knowledge import Znanie
from ...forms.admin_interview_work_form import InterviewAnswerExpertProposalForms


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
        tz_obj = Tz.objects.get(name='Вопрос')

        for elm in self.object_list:
            category = elm.category.name
            title = elm.name
            questions = Relation.objects.select_related('rz').filter(Q(bz__pk=elm.pk) & Q(rz__tz=tz_obj)).values('rz')
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
        tz_obj = Tz.objects.get(name='Вопрос')
        questions = Relation.objects.filter(Q(bz=self.object) & Q(rz__tz=tz_obj)).values('rz', 'rz__name')

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


@login_required
def question_admin_work_view(request, inter_pk, quest_pk):
    """
        Выводит таблицу с данными о всех предложениях экспертов интервью
    """
    chek_is_stuff(request.user)
    context = dict()
    interview = Znanie.objects.values('pk', 'name').get(pk=inter_pk)
    context['interview_name'] = interview.get('name')
    period = Relation.objects.select_related('tr', 'rz').filter(
        Q(bz__pk=interview.get('pk')) & Q(tr__name='Период интервью')
    ).first().rz.name

    question = Znanie.objects.values('name').get(pk=quest_pk)
    context['question_name'] = question.get('name')
    context['period'] = f"с {period}".replace('-', 'по')

    queryset = InterviewAnswerExpertProposal.objects.filter(question__pk=quest_pk, interview__pk=inter_pk)
    InterviewAnswerExpertFormSet = modelformset_factory(InterviewAnswerExpertProposal, extra=0,
                                                        form=InterviewAnswerExpertProposalForms)
    if request.method == 'POST':
        formset = InterviewAnswerExpertFormSet(request.POST, queryset=queryset)
        if formset.is_valid():
            for form in formset:
                obj = form.save(commit=False)
                status = obj.status
                answer = obj.new_answer
                comment = obj.admin_comment
                # Проверка на наличие изменений в записи
                if (status == form.old_status) and (answer == form.old_answer) and (comment and form.old_comment):
                    continue
                if form.old_status != status:
                    # Если админ изменил статус на "Принят",
                    # то создаётся новое знание и связь на основе введённых админом данных
                    if status == 'APPRVE':
                        if not form.cleaned_data.get('admin_comment'):
                            messages.error(request, 'Не указана тема знания.')
                            break
                        admin_comment = obj.admin_comment
                        if '~' in admin_comment:
                            knowledge_name, knowledge_content = admin_comment.split('~')
                        else:
                            knowledge_name, knowledge_content = admin_comment, None
                        tz = Tz.objects.filter(name='Тезис').first()
                        author, is_created = Author.objects.get_or_create(name=obj.expert.get_full_name)
                        new_knowledge = Znanie.objects.create(
                            name=knowledge_name,
                            content=knowledge_content,
                            tz=tz,
                            author=author,
                            user=obj.expert,
                            is_published=True
                        )
                        if obj.question.tz.name == 'Вопрос':
                            tr = Tr.objects.get(name='Ответ [ы]')
                        else:
                            tr = Tr.objects.get(name='Аргумент [ы]')
                        Relation.objects.create(
                            bz=obj.question,
                            rz=new_knowledge,
                            tr=tr,
                            author=author,
                            user=obj.expert,
                            is_published=True
                        )
                        obj.new_answer = new_knowledge
                        obj.status = 'APPRVE'
                    # Если админ изменил статус на "Не принят",
                    elif status == 'REJECT':
                        obj.status = 'REJECT'
                # Если админ указал только ответ из списка существующих/новых ответов, то статус устанавливается сам,
                elif not status and obj.new_answer:
                    existing_answer = obj.new_answer
                    # Если дата создания выбранного ответа меньше даты создания
                    # предложения эксперта, то статус "Дублирует ответ", иначе "Дублирует предложение"
                    if existing_answer.date < form.instance.updated.date():
                        obj.status = 'ANSDPL'
                    else:
                        obj.status = 'RESDPL'
                obj.admin_reviewer = request.user
                obj.save()
            return redirect('question_admin_work', inter_pk=inter_pk, quest_pk=quest_pk)
    else:
        formset = InterviewAnswerExpertFormSet(queryset=queryset)
    context['questions'] = list(zip(queryset, formset))
    context['formset'] = formset
    context['backup_url'] = reverse_lazy('interview_quests', kwargs={'pk': inter_pk})
    return render(request, 'drevo/admin_interview_work_page/question_admin_work.html', context)
