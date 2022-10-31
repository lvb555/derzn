from django.views.generic import DetailView
from datetime import datetime

from users.models import Favourite
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

    # если знание является тестом - переводит на другой шаблон
    def get_template_names(self):
        if self.object.tz in Tz.objects.filter(name='Тест'):
            return ['drevo/testirovanie_detail.html']
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

        context['rels'] = [[item.name, qs.filter(tr=item, rz__is_published=True)]
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
        der = get_children_by_relation_type_for_knowledge(
            knowledge)
        context['button'] = []
        for child, rez in der.items():
            if child.pk == 24:
                context['button'].append(rez)

        # создает контекст, в котором "внуки" знания, если это знание - тест
        if self.object.tz in Tz.objects.filter(name='Тест'):

            context['pwe'] = {}
            context['pravotvet'] = {}
            for i in context['rels']:

                for item in i[1]:

                    zn = item.rz.pk

                    knowledge1 = Znanie.objects.get(pk=zn)

                    context['pwe'][str(item.rz)] = get_children_for_knowledge(
                        knowledge1)
                    c = get_children_by_relation_type_for_knowledge(
                        knowledge1)

                    for child, rez in c.items():
                        if child.pk == 26:
                            context['pravotvet'][str(item.rz)] = rez

        return context
