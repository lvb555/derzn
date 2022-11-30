from django.views.generic import DetailView
from datetime import datetime
from drevo.models.label_feed_message import LabelFeedMessage

from users.models import Favourite, User
from ..models import Znanie, Relation, Tr, IP, Visits, Comment, BrowsingHistory, Tz
from loguru import logger
from ..relations_tree import (get_category_for_knowledge, get_ancestors_for_knowledge,
                              get_siblings_for_knowledge,
                              get_children_by_relation_type_for_knowledge, get_children_for_knowledge)
import humanize


logger.add('logs/main.log',
           format="{time} {level} {message}", rotation='100Kb', level="ERROR")


class ZnanieDetailView(DetailView):
    """
    Выводит подробную информацию о сущности Знание
    """
    model = Znanie
    context_object_name = 'znanie'

    def get_template_names(self):
        if self.object.tz in Tz.objects.filter(name='Тест'):
            return ['drevo/quiz_detail.html']
        else:
            return ['drevo/znanie_detail.html']

    def get_context_data(self, *, object_list=None, **kwargs):
        """
        Передает в шаблон данные через контекст
        """
        context = super().get_context_data(**kwargs)

        # первичный ключ текущей записи
        pk = self.object.pk

        # получаем список связей, в который базовым знанием является текущее знание
        qs = Relation.objects.filter(bz__pk=pk)

        # получаем список всех видов связей
        ts = Tr.objects.all()

        context['rels'] = [[item.name, qs.filter(tr=item, rz__is_published=True).prefetch_related('rz')]
                           for item in ts if qs.filter(tr=item, rz__is_published=True).count() > 0]

        # сохранение ip пользователя
        knowledge = Znanie.objects.get(pk=pk)
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        if not IP.objects.filter(ip=ip):
            IP.objects.create(ip=ip)
        if knowledge not in IP.objects.get(ip=ip).visits.all() and self.request.user.is_anonymous:
            IP.objects.get(ip=ip).visits.add(knowledge)

        IP.objects.get(ip=ip).save()

        # добавление просмотра
        if self.request.user.is_authenticated:
            if not Visits.objects.filter(znanie=knowledge, user=self.request.user).count():
                Visits.objects.create(
                    znanie=knowledge, user=self.request.user).save()
        
        # добавление историю просмотра
        if self.request.user.is_authenticated:
            if not BrowsingHistory.objects.filter(znanie=knowledge, user=self.request.user).count():
                BrowsingHistory.objects.create(
                    znanie=knowledge, user=self.request.user, date=datetime.now()).save()
            else:
                browsing_history_obj = BrowsingHistory.objects.get(znanie=knowledge, user=self.request.user)
                browsing_history_obj.date = datetime.now()
                browsing_history_obj.save()

        # формируем дерево категорий для категории текущего знания
        category = get_category_for_knowledge(knowledge)
        if category:
            categories = category.get_ancestors(
                ascending=False, include_self=True)
        else:
            categories = []
        context['category'] = category
        context['categories'] = categories
        context['chain'] = get_ancestors_for_knowledge(knowledge)
        context['siblings'] = get_siblings_for_knowledge(knowledge)
        # context['children'] = get_children_for_knowledge(knowledge)
        context['children_by_tr'] = get_children_by_relation_type_for_knowledge(
            knowledge)
        context['visits'] = Visits.objects.filter(
            znanie=knowledge).count() + knowledge.ip_set.all().count()

        user = self.request.user
        if user.is_authenticated:
            user_favourite = Favourite.objects.filter(user=user)
            if user_favourite.exists():
                context['user_favourite'] = user_favourite.first().favourites.filter(id=self.object.id).exists()

            user_vote = knowledge.get_users_vote(user)
            if user_vote:
                context['user_vote'] = {user_vote: True}

        context['likes_count'] = humanize.intword(knowledge.get_likes_count())
        context['dislikes_count'] = humanize.intword(
            knowledge.get_dislikes_count())
        context['comment_max_length'] = Comment.CONTENT_MAX_LENGTH

        context['table'] = knowledge.get_table_object()

        # возвращает кнопку прохождения тестирования, если знание- базовое для теста

        context['button'] = []
        for relation, children in context['children_by_tr'].items():
            if relation.pk == 24:
                context['button'].append(children)

        # создает контекст, в котором "внуки" знания, если это знание - тест
        if self.object.tz in Tz.objects.filter(name='Тест'):

            context['all_answers_and_questions'] = {}
            context['right_answer'] = {}
            for relation_name, relations in context['rels']:

                for item in relations:

                    context['all_answers_and_questions'][str(item.rz)] = get_children_for_knowledge(
                        item.rz).order_by('-pk')
                    grandson = get_children_by_relation_type_for_knowledge(
                        item.rz)

                    for question, answer in grandson.items():
                        if question.pk == 26:
                            context['right_answer'][str(item.rz)] = answer
            context['all_answers_and_questions'] = dict(sorted(context['all_answers_and_questions'].items(),
                                                               key=lambda a: a, reverse=True))


        labels = LabelFeedMessage.objects.all()
        context['labels'] = labels

        # создание списка для отображения в блоке отправления
        try:
            user = User.objects.get(id = self.request.user.id)
            my_friends = user.user_friends.all().prefetch_related('profile') # те, кто в друзьях у меня
            i_in_friends = user.users_friends.all().prefetch_related('profile') # те, у кого я в друзьях
            
            all_friends = my_friends.union(i_in_friends, all=False)
            context['friends'] = all_friends
            context['friends_count'] = len(all_friends)
        
        # ошибка в случае открытия страницы пользователем без аккаунта - обработка ситуации в html-странице 
        except TypeError:
            pass

        return context
