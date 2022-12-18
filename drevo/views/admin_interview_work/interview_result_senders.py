from django.conf import settings
from django.db.models import F, Q
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from ...models import Relation, Tr
from ...sender import send_email


class InterviewResultSender:
    def __init__(self, proposals, interview_name, question_name, interview_pk=None, question_pk=None):
        self.proposals = proposals
        self.interview_name = interview_name
        self.question_name = question_name
        self.interview_pk = interview_pk
        self.question_pk = question_pk

    def start_mailing(self) -> bool:
        try:
            self._send_results_experts()
            if self.proposals.filter(status='APPRVE').exists():
                pass
                self._send_new_answers()
            return True
        except Exception as error:
            print(f'Error while mailing experts: {error}')
            return False

    def _send_results_experts(self) -> None:
        """
            Функция для рассылки результатов интервью экспертам
        """
        interview_url_kwargs = {'interview_pk': self.interview_pk, 'question_pk': self.question_pk}
        interview_url = f"{settings.BASE_URL}{reverse_lazy('question_expert_work', kwargs=interview_url_kwargs)}"

        experts_pk = set(self.proposals.values_list('expert', flat=True))
        for expert_pk in experts_pk:
            expert_proposals = self.proposals.filter(expert__pk=expert_pk)
            proposals_data = {
                'accepted': expert_proposals.filter(status='APPRVE'),
                'not_accepted': expert_proposals.filter(status='REJECT'),
                'duplicates': expert_proposals.filter(Q(status='ANSDPL') | Q(status='RESDPL'))
            }

            context = dict(
                interview_name=self.interview_name,
                question_name=self.question_name,
                proposals_data=proposals_data,
                interview_url=interview_url
            )
            expert_obj = expert_proposals.first().expert
            email_address = expert_obj.email
            message_subject = 'Результаты интервью!'
            context['expert'] = expert_obj
            message_html = render_to_string('email_templates/interview_result_email/interview_results_email.html',
                                            context)
            send_email(email_address, message_subject, message_html, message_html)

    def _send_new_answers(self) -> None:
        """
            Функция для рассылки уведомлений экспертам о появлении новых ответов на интервью
        """
        experts = self.proposals.values(
            first_name=F('expert__first_name'), last_name=F('expert__last_name'), email=F('expert__email')
        ).order_by().distinct()
        new_answers = self.proposals.filter(status='APPRVE').values_list('new_answer__name', flat=True)
        tr_obj = Tr.objects.get(name='Ответ [ы]')
        answers = Relation.objects.select_related('bz', 'rz').filter(
            Q(bz__name=self.question_name) & Q(tr=tr_obj)
        ).values_list('rz__name', flat=True)

        context = dict(
            interview_name=self.interview_name,
            question_name=self.question_name,
            answers=answers,
            new_answers=new_answers
        )

        for expert in experts:
            email_address = expert.get('email')
            message_subject = 'Новые ответы!'
            context['expert'] = expert
            message_html = render_to_string('email_templates/interview_result_email/interview_new_answer_email.html',
                                            context)
            send_email(email_address, message_subject, message_html, message_html)
