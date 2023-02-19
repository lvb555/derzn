import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.forms import modelformset_factory
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse_lazy, reverse
from django.utils.timezone import now
from django.views.generic import ListView, DetailView, UpdateView, RedirectView
from ...models import Relation, Tz, Author, Tr, SpecialPermissions
from ...models.interview_answer_expert_proposal import InterviewAnswerExpertProposal
from ...models.knowledge import Znanie
from ...models.interview_results_schedule import InterviewResultsSendingSchedule
from ...models.settings_options import SettingsOptions
from ...forms.admin_interview_work_form import InterviewAnswerExpertProposalForms
from .interview_result_senders import InterviewResultSender
from ...forms.knowledge_form import ZnanieForm
from datetime import date


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
                    Q(interview=elm) & Q(question__pk=quest.get('rz')) & Q(status=None)
                ).exclude(new_answer_text__isnull=True).exclude(new_answer_text__exact='')
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
        questions = Relation.objects.select_related('rz').filter(
            Q(bz=self.object) & Q(rz__tz=tz_obj)
        ).order_by('-rz__order', 'rz__name').values('rz', 'rz__name')

        data = []

        for quest in questions:
            status = 'success'
            danger_cnt = None
            exp_prop = InterviewAnswerExpertProposal.objects.filter(
                Q(interview__pk=self.kwargs['pk']) & Q(question__pk=quest.get('rz')) & Q(status=None)
            ).exclude(new_answer_text__isnull=True).exclude(new_answer_text__exact='')
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
    interview = Znanie.objects.get(pk=inter_pk)
    context['interview'] = interview
    period = Relation.objects.select_related('tr', 'rz').filter(
        Q(bz__pk=interview.pk) & Q(tr__name='Период интервью')
    ).first().rz.name

    question = Znanie.objects.values('pk', 'name').get(pk=quest_pk)
    context['question'] = question
    context['period'] = f"с {period}".replace('-', 'по')

    start_day, start_month, start_year = period.replace('-', ' ').split(' ')[0].split('.')
    start_date = date(int(f'20{start_year}'), int(start_month), int(start_day))
    context['interview_start_date'] = start_date

    if not InterviewResultsSendingSchedule.objects.filter(interview=interview).exists():
        interview_schedule = InterviewResultsSendingSchedule(interview=interview)
        interview_schedule.is_interview()
        interview_schedule.save()
    else:
        interview_schedule = InterviewResultsSendingSchedule.objects.get(interview=interview)

    if now() >= interview_schedule.next_sending:
        context['mailing_available'] = True
    context['last_sending'] = interview_schedule.last_sending

    context['cur_filter'] = request.GET.get('filter')

    answers = Relation.objects.select_related('rz', 'tr').filter(
        bz__pk=quest_pk, tr__name='Ответ [ы]'
    ).order_by('rz__name', 'rz__order')

    def expert_to_author(expert) -> Author:
        """
            Функция для создания автора по эксперту
        """
        authors = Author.objects.filter(user_author=expert)
        if authors.exists():
            return authors.first()
        return Author.objects.create(name=expert.get_full_name, user_author=expert)

    def get_queryset():
        filter_by = request.GET.get('filter')
        queryset_obj = InterviewAnswerExpertProposal.objects\
            .select_related('interview', 'answer', 'expert', 'question', 'new_answer')\
            .filter(question__pk=quest_pk, interview__pk=inter_pk)\
            .exclude(new_answer_text__isnull=True).exclude(new_answer_text__exact='')\
            .order_by('expert__first_name', '-updated')
        if filter_by:
            return queryset_obj.filter(status=filter_by) if filter_by != 'None' else queryset_obj.filter(status=None)
        return queryset_obj

    queryset = get_queryset()
    InterviewAnswerExpertFormSet = modelformset_factory(InterviewAnswerExpertProposal, extra=0,
                                                        form=InterviewAnswerExpertProposalForms)

    if request.method == 'POST':
        formset = InterviewAnswerExpertFormSet(request.POST, queryset=queryset)
        if formset.is_valid():
            for form in formset:
                obj = form.save(commit=False)

                status = obj.status
                answer_pk = request.POST.get(f'expert-{obj.pk}-answer', 'None')
                if answer_pk != 'None':
                    answer = answers.get(rz__pk=answer_pk).rz
                else:
                    answer = None
                comment = obj.admin_comment
                # Проверка на наличие изменений в записи
                if form.old_status is not None:
                    continue

                # На случай если эксперт был уведомлён о предложении, когда она было не обработано, необходимо вернуть
                # is_notified в False, так как теперь оно обработано и необходимо оповестить об этом эксперта
                if obj.is_notified:
                    obj.is_notified = False

                # Если админ изменил статус на "Принят",
                # то создаётся новое знание и связь на основе введённых админом данных
                if (form.old_status != status) and status == 'APPRVE':
                    # Обрабатывать ошибку на существующее знание
                    if not form.cleaned_data.get('admin_comment'):
                        messages.error(request, f'Предложение  №{obj.pk}: Не указана тема знания.')
                        continue
                    if '~' in comment:
                        knowledge_name, knowledge_content = comment.split('~')
                    else:
                        knowledge_name, knowledge_content = comment, None
                    if Znanie.objects.filter(name=knowledge_name).exists():
                        messages.error(request, f'Предложение  №{obj.pk}: Знание с такой темой уже существует.')
                        continue
                    tz = Tz.objects.filter(name='Тезис').first()
                    author = expert_to_author(obj.expert)
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
                    if obj.is_agreed:
                        obj.answer = new_knowledge
                    obj.admin_reviewer = request.user
                    obj.save()
                    redirect_url = reverse(
                        'admin_knowledge_edit',
                        kwargs={'inter_pk': inter_pk, 'quest_pk': quest_pk, 'znanie_pk': new_knowledge.pk}
                    )
                    return redirect(redirect_url)

                # Если админ указал только ответ из списка существующих/новых ответов, то статус устанавливается сам,
                if not status and answer:
                    # Если дата создания выбранного ответа меньше даты создания
                    # интервью, то статус "Дублирует ответ", иначе "Дублирует предложение"
                    obj.status = 'ANSDPL' if answer.date <= start_date else 'RESDPL'
                    obj.duplicate_answer = answer

                if ((form.old_status != status) and status == 'REJECT') and obj.is_agreed:
                    # Если эксперт выбрал свой ответ и он был отклонён,
                    # то устанавливаем связь его ответа со знанием 'Другое'

                    # Создаём знание "Другое" если его нет
                    other_obj, _ = Znanie.objects.get_or_create(
                        name='Другое',
                        tz=Tz.objects.get(name='Другое'),
                        user=request.user,
                        is_published=True
                    )
                    # Устанавливаем связь знания "Другое" с вопросом
                    if not Relation.objects.filter(bz=obj.question, rz=other_obj, user=obj.expert).exists():
                        Relation.objects.update_or_create(
                            bz=obj.question,
                            rz=other_obj,
                            tr=Tr.objects.get(name='Ответ [ы]'),
                            author=expert_to_author(obj.expert),
                            user=obj.expert,
                            is_published=True
                        )

                obj.admin_reviewer = request.user
                obj.save()

            if 'save_input' in request.POST:
                request.session['is_saved'] = True
            if now() >= interview_schedule.next_sending:
                redirect_url = f"{reverse('admin_notify_experts', kwargs={'inter_pk': inter_pk, 'quest_pk': quest_pk})}"
                return redirect(redirect_url)
            redirect_url = f"{reverse('question_admin_work', kwargs={'inter_pk': inter_pk, 'quest_pk': quest_pk})}"
            if context.get('cur_filter'):
                get_params = f"?filter={context.get('cur_filter')}"
                return redirect(f'{redirect_url}{get_params}')
            return redirect(redirect_url)
    else:
        formset = InterviewAnswerExpertFormSet(queryset=queryset)
    context['answers_list'] = [(None, '------')] + \
                              [(elm.get('rz__pk'), elm.get('rz__name')) for elm in answers.values('rz__pk', 'rz__name')]
    context['status_list'] = InterviewAnswerExpertProposal.STATUSES
    context['questions'] = list(zip(queryset, formset))
    context['formset'] = formset
    context['backup_url'] = reverse_lazy('interview_quests', kwargs={'pk': inter_pk})

    if 'is_saved' in request.session.keys():
        context['is_saved'] = request.session['is_saved']
        del request.session['is_saved']
    if 'is_notified' in request.session.keys():
        context['is_notified'] = request.session['is_notified']
        del request.session['is_notified']
    return render(request, 'drevo/admin_interview_work_page/question_admin_work.html', context)


class AdminEditingKnowledgeView(UpdateView):
    """
        Представление для старницы редактирования знания, созданного на основе предложения эксперта
    """
    model = Znanie
    template_name = 'drevo/admin_interview_work_page/editing_knowledge.html'
    form_class = ZnanieForm
    pk_url_kwarg = 'znanie_pk'

    def get_success_url(self):
        inter_pk, quest_pk = self.kwargs.get('inter_pk'), self.kwargs.get('quest_pk')
        return reverse('question_admin_work', kwargs={'inter_pk': inter_pk, 'quest_pk': quest_pk})

    def dispatch(self, request, *args, **kwargs):
        chek_is_stuff(request.user)
        return super(AdminEditingKnowledgeView, self).dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        form = super(AdminEditingKnowledgeView, self).get_form()
        for field in form.fields.keys():
            if field not in ['is_published', 'is_send', 'show_link']:
                form.fields[field].widget.attrs['class'] = 'form-control'
        return form

    def get_context_data(self, **kwargs):
        context = super(AdminEditingKnowledgeView, self).get_context_data(**kwargs)
        interview = Znanie.objects.get(pk=self.kwargs.get('inter_pk'))
        question = Znanie.objects.get(pk=self.kwargs.get('quest_pk'))
        context['knowledge_name'] = self.object.name
        context['interview_name'] = interview.name
        context['question_name'] = question.name
        return context


class NotifyExpertsView(RedirectView):
    """
        Представление для начала рассылки о результатах интервью
    """
    def get_redirect_url(self, *args, **kwargs):
        inter_pk, quest_pk = self.kwargs.get('inter_pk'), self.kwargs.get('quest_pk')
        return reverse('question_admin_work', kwargs={'inter_pk': inter_pk, 'quest_pk': quest_pk})

    def get(self, request, *args, **kwargs):
        inter_pk, quest_pk = self.kwargs.get('inter_pk'), self.kwargs.get('quest_pk')
        interview_obj = Znanie.objects.select_related('category').get(pk=inter_pk)

        # Получаем все обработанные и необработанные предложения,
        # которые были у данного интервью и c неотправленными уведомлениями
        proposals = InterviewAnswerExpertProposal.objects.select_related('expert', 'new_answer', 'question').filter(
            Q(interview__pk=inter_pk) & Q(is_notified=False)
        ).order_by('question__name', '-updated')

        if proposals.exists():
            # Получаем категорию(компетенцию интервью) и всех экспертов данной компетенции
            inter_competence = interview_obj.category
            experts = [
                cat_exp.expert
                for cat_exp in
                SpecialPermissions.objects.select_related('expert').filter(categories__pk=inter_competence.pk)
            ]

            sender = InterviewResultSender(
                experts=experts,
                proposals=proposals,
                interview=interview_obj
            )
            if sender.start_mailing():
                notified_proposals = list()
                for obj in proposals:
                    obj.is_notified = True
                    notified_proposals.append(obj)
                InterviewAnswerExpertProposal.objects.bulk_update(notified_proposals, ['is_notified'])
                request.session['is_notified'] = True
                schedule = InterviewResultsSendingSchedule.objects.get(interview__pk=inter_pk)
                # Увеличиваем время следующей рассылки на NOT_MORE_OFTEN часов
                not_more_often, _ = SettingsOptions.objects.get_or_create(
                    name='Не чаще (часов)',
                    admin=True,
                    defaults={'default_param': '1'},
                )
                schedule.next_sending = now() + datetime.timedelta(hours=int(not_more_often.default_param))
                schedule.save()
        return super(NotifyExpertsView, self).get(request, *args, **kwargs)
