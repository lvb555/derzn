from django.db.models import F, Q
from django.template.loader import render_to_string
from ...models import Relation, Tr, InterviewAnswerExpertProposal, Tz
from ...sender import send_email


class InterviewResultSender:
    def __init__(self, experts, proposals, interview):
        self.experts = experts
        self.proposals = proposals
        self.interview = interview

    def start_mailing(self) -> bool:
        try:
            self._send_results()
            return True
        except Exception as error:
            print(f'Error while mailing experts: {error}')
            return False

    def _send_results(self):
        """
            Метод для рассылки результатов интервью экспертам
        """
        context = dict(interview=self.interview)
        second_part_is_created, second_part_data = self._create_message_second_part()
        context.update(second_part_data)

        for expert in self.experts:
            context['expert'] = expert
            first_part_is_created, first_part_data = self._create_message_first_part(expert=expert)
            context.update(first_part_data)

            if first_part_is_created or second_part_is_created:
                context['first_part_is_created'] = first_part_is_created
                context['second_part_is_created'] = second_part_is_created

                email_address = expert.email
                message_subject = 'Результаты интервью!'
                message_html = render_to_string(
                    'email_templates/interview_result_email/interview_results_email.html',
                    context
                )
                send_email(email_address, message_subject, message_html, message_html)

    def _create_message_first_part(self, expert):
        """
            Метод для создания первой части сообщения
        """
        # Получаем все предложения эксперта по данному интервью
        proposals_all = InterviewAnswerExpertProposal.objects.select_related('expert', 'new_answer', 'question').filter(
            Q(interview__pk=self.interview.pk) & Q(expert=expert)
        ).order_by('question__name', '-updated')
        # Получаем предложения эксперта о которых он не был уведомлён
        proposals_un_notified = self.proposals.filter(expert=expert)

        # Проверка на наличие предложений со статусом
        if not proposals_un_notified.filter(~Q(status=None)).exists():
            return False, dict()

        # Получаем все вопросы интервью
        interview_questions = Relation.objects.select_related('rz').filter(
            Q(bz=self.interview) & Q(rz__tz=Tz.objects.get(name='Вопрос'))
        ).order_by('-rz__order').values_list('rz__name', flat=True)

        proposals_data = {question: None for question in interview_questions}

        first_part_data = dict()

        # Разделяем предложения по вопросам и статусам
        for proposal in proposals_all:
            question = proposal.question.name
            if proposals_data.get(question) is None:
                proposals_data[question] = {
                    'accepted': list(),
                    'duplicates': list(),
                    'not_accepted': list(),
                    'unprocessed': list()
                }
            if not proposal.status:
                proposals_data[question]['unprocessed'].append(proposal)
                continue
            if proposal.status == 'APPRVE':
                proposals_data[question]['accepted'].append(proposal)
            if proposal.status == 'ANSDPL' or proposal.status == 'RESDPL':
                proposals_data[question]['duplicates'].append(proposal)
            else:
                proposals_data[question]['not_accepted'].append(proposal)

        many_questions = True
        if len(proposals_data.keys()) == 1:
            many_questions = False
            question_name = list(proposals_data.keys())[0]
            first_part_data['question_name'] = question_name
            first_part_data['proposal_count'] = len(proposals_all)

        first_part_data['many_questions'] = many_questions
        first_part_data['proposals_data'] = proposals_data
        first_part_data['proposals_un_notified'] = proposals_un_notified
        return True, first_part_data

    def _create_message_second_part(self):
        """
            Метод для создания второй части сообщения
        """
        # Получаем новые ответы
        new_answers = self.proposals.filter(status='APPRVE').values_list('new_answer__name', flat=True)
        if not new_answers:
            return False, dict()

        # Получаем список всех вопросов интервью
        interview_questions = Relation.objects.select_related('rz').filter(
            Q(bz=self.interview) & Q(rz__tz=Tz.objects.get(name='Вопрос'))
        ).order_by('-rz__order').values_list('rz__name', flat=True)

        answers_data = {question: None for question in interview_questions}  # {question: [answers...]}

        # Разделяем ответы по вопросам
        for question in interview_questions:
            # Получаем все ответы по вопросу интервью
            answers_data[question] = Relation.objects.select_related('bz', 'rz').prefetch_related('rz__author').filter(
                Q(bz__name=question) & Q(tr=Tr.objects.get(name='Ответ [ы]'))
            ).order_by('-rz__order').values(answer_name=F('rz__name'), author_name=F('rz__author__name'))

        return True, dict(new_answers=new_answers, answers_data=answers_data)
