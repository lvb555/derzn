from django.views.generic import DetailView
from datetime import datetime
from ..models import Znanie, IP, Visits, BrowsingHistory, Relation, Tr
from loguru import logger
from ..relations_tree import get_children_by_relation_type_for_knowledge

logger.add('logs/main.log',
           format="{time} {level} {message}", rotation='100Kb', level="ERROR")


class AlgorithmDetailView(DetailView):
    model = Znanie
    context_object_name = 'znanie'
    template_name = "drevo/algorithm_detail.html"

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
            browsing_history_obj, created = BrowsingHistory.objects.get_or_create(znanie=knowledge,
                                                                                  user=self.request.user)
            if not created:
                browsing_history_obj.date = datetime.now()
                browsing_history_obj.save()

        # Создание словаря со всеми элементами алгоритма
        start_of_algorithm = Relation.objects.get(bz=knowledge, tr__name='Начало алгоритма').rz
        context['algorithm_data'] = make_complicated_dict1({'previous_key': []}, start_of_algorithm, 'previous_key')
        context['algorithm_data'] = context['algorithm_data']['previous_key']

        return context


try:
    next_relation = Tr.objects.get(name='Далее')
except Tr.DoesNotExist:
    next_relation = None


def make_complicated_dict1(algorithm_dict, queryset, previous_key, level=1):
    """
    Рекурсивно ищет потомков текущего знания до тех пор,
    пока функция get_children_by_relation_type_for_knowledge не вернет None
    """
    relations = get_children_by_relation_type_for_knowledge(queryset)
    if relations:
        if next_relation in relations.keys() and len(relations) == 1:
            if level == 0:
                algorithm_dict.append(queryset)
                for relation, elem in relations.items():
                    make_complicated_dict1(algorithm_dict, elem[0], elem[0], level=0)
            else:
                algorithm_dict[previous_key].append(queryset)
                for relation, elem in relations.items():
                    make_complicated_dict1(algorithm_dict[previous_key], elem[0], elem[0], level=0)
        else:
            if level == 0:
                algorithm_dict.append({queryset: []})
                last_direction = None
                for relation, elem in relations.items():
                    if relation.name == 'Далее':
                        last_direction = elem[0]
                    else:
                        for el in elem:
                            make_complicated_dict1(algorithm_dict[len(algorithm_dict) - 1], el, queryset, level=1)
                if last_direction:
                    make_complicated_dict1(algorithm_dict, last_direction, previous_key, level=0)
            else:
                algorithm_dict[previous_key].append({queryset: []})
                last_direction = None
                for relation, elem in relations.items():
                    if relation.name == 'Далее':
                        last_direction = elem[0]
                    else:
                        for el in elem:
                            make_complicated_dict1(algorithm_dict[previous_key][len(algorithm_dict[previous_key]) - 1],
                                                   el, queryset, level=1)
                if last_direction:
                    make_complicated_dict1(algorithm_dict[previous_key], last_direction, previous_key, level=0)
    else:
        if level == 0:
            algorithm_dict.append(queryset)
        else:
            algorithm_dict[previous_key].append(queryset)

    return algorithm_dict
