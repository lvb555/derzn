from django.views.generic import DetailView
from datetime import datetime
from ..models import Znanie, IP, Visits, BrowsingHistory
from loguru import logger
from ..relations_tree import (get_children_by_relation_type_for_knowledge, get_children_for_knowledge)


logger.add('logs/main.log',
           format="{time} {level} {message}", rotation='100Kb', level="ERROR")


class QuizDetailView(DetailView):

    model = Znanie
    context_object_name = 'znanie'
    template_name = "drevo/quiz_detail.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        """
        Передает в шаблон данные через контекст
        """
        context = super().get_context_data(**kwargs)

        # первичный ключ текущей записи
        pk = self.object.pk

        # сохранение ip пользователя
        knowledge = Znanie.objects.get(pk=pk)
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        ip_obj, created = IP.objects.get_or_create(ip=ip)
        if knowledge not in ip_obj.visits.all() and self.request.user.is_anonymous:
            ip_obj.visits.add(knowledge)


        # добавление просмотра
        if self.request.user.is_authenticated:
            Visits.objects.create(znanie=knowledge, user=self.request.user)


        # добавление историю просмотра
        if self.request.user.is_authenticated:
            browsing_history_obj, created = BrowsingHistory.objects.get_or_create(znanie=knowledge, user=self.request.user)
            if not created:
                browsing_history_obj.date = datetime.now()
                browsing_history_obj.save()


        context['children'] = get_children_for_knowledge(knowledge)
        context['all_answers_and_questions'] = {}
        context['right_answer'] = {}

        for item in context['children'].order_by('order'):
            context['all_answers_and_questions'][str(item)] = get_children_for_knowledge(
                item).order_by('order')
            grandson = get_children_by_relation_type_for_knowledge(
                item)
            if grandson:
                for question, answer in reversed(grandson.items()):
                    if question.name == 'Ответ верный':
                        context['right_answer'][str(item) + ' ' + str(item.pk)] = answer
            else:
                context['right_answer'][str(item) + ' ' + str(item.pk)] = 'На этот вопрос еще нет ответа'

        return context
