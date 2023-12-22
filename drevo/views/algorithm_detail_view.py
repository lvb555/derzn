import json
from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView
from datetime import datetime
from django.views.generic.edit import ProcessFormView
from ..models import Znanie, IP, Visits, BrowsingHistory, Relation, Tr , AlgorithmAdditionalElements
from loguru import logger
from ..models.algorithms_data import AlgorithmData, AlgorithmWork
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

            context['previous_works'] = AlgorithmWork.objects.filter(user=self.request.user, algorithm=knowledge)\
                .values_list('work_name', flat=True)

            if previous_works := self.request.GET.get('previous_works'):
                context['progress'] = list(AlgorithmData.objects.filter(user=self.request.user, algorithm=knowledge,
                                                                      work__work_name=previous_works).values(
                                                                        'element', 'element_type'))
                if self.request.GET.get('previous_works'):
                    context['current_work'] = self.request.GET.get('previous_works')

            if self.request.GET.get('mode'):
                context['modification'] = 'on'

            # В случае, если у знания может быть лишь одна работа - сразу загружаем пользовательский прогресс
            if not knowledge.several_works:
                context['progress'] = list(AlgorithmData.objects.filter(user=self.request.user, algorithm=knowledge,
                                                                        work__work_name='Данные по алгоритму').values(
                                                                        'element', 'element_type'))

        # Создание словаря со всеми элементами алгоритма
        start_of_algorithm = Relation.objects.get(bz=knowledge, tr__name='Начало алгоритма').rz
        try:
            next_relation = Tr.objects.get(name='Далее')
        except Tr.DoesNotExist:
            next_relation = None
        context['algorithm_data'] = make_complicated_dict1(
            {'previous_key': []},
            start_of_algorithm,
            'previous_key',
            next_relation=next_relation
        )
        context['algorithm_data'] = context['algorithm_data']['previous_key']

        return context


def make_complicated_dict1(algorithm_dict, queryset, previous_key, level=1, next_relation=None):
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
                            make_complicated_dict1(algorithm_dict[len(algorithm_dict) - 1], el, queryset, level=1,
                                                   next_relation=next_relation)
                if last_direction:
                    make_complicated_dict1(algorithm_dict, last_direction, previous_key, level=0, next_relation=next_relation)
            else:
                algorithm_dict[previous_key].append({queryset: []})
                last_direction = None
                for relation, elem in relations.items():
                    if relation.name == 'Далее':
                        last_direction = elem[0]
                    else:
                        for el in elem:
                            make_complicated_dict1(algorithm_dict[previous_key][len(algorithm_dict[previous_key]) - 1],
                                                   el, queryset, level=1, next_relation=next_relation)
                if last_direction:
                    make_complicated_dict1(algorithm_dict[previous_key], last_direction, previous_key, level=0,
                                           next_relation=next_relation)
    else:
        if level == 0:
            algorithm_dict.append(queryset)
        else:
            algorithm_dict[previous_key].append(queryset)

    return algorithm_dict


class AlgorithmResultAdd(ProcessFormView):
    def get(self, request, pk, *args, **kwargs):
        if request.is_ajax():
            user = self.request.user

            if not user.is_authenticated:
                return JsonResponse({}, status=403)

            if pk:
                algorithm = get_object_or_404(Znanie, id=pk)
                saved_progress = json.loads(request.GET.get('values'))
                new_elements = json.loads(request.GET.get('new_elements'))
                deleted_elements = json.loads(request.GET.get('deleted'))
                redacted_elements = json.loads(request.GET.get('redacted'))
                work_name = request.GET.get('work')
                previous_result = request.GET.get('previous_result')
                previous_work = AlgorithmWork.objects.filter(algorithm=algorithm, user=user, 
                                                             work_name=str(previous_result)).first()

                if previous_result != '' and previous_work:
                    if not new_elements and not deleted_elements and not redacted_elements:
                        results_for_delete = AlgorithmData.objects.filter(work=previous_work)
                        results_for_delete.delete()
                else:
                    previous_work = AlgorithmWork.objects.create(
                                        algorithm=algorithm,
                                        user=user,
                                        work_name=work_name,
                                    )

                for algorithm_element in saved_progress:
                    AlgorithmData.objects.create(
                        algorithm=algorithm,
                        user=user,
                        element=str(algorithm_element[0]),
                        element_type=algorithm_element[1],
                        work=previous_work,
                    )

                for deleted_element in deleted_elements:
                    elem = get_object_or_404(AlgorithmAdditionalElements, user=user, algorithm=algorithm,
                                             work=previous_work, element_name=str(deleted_element))
                    elem.delete()
                    try:
                        saved_in_progress_element = get_object_or_404(AlgorithmData, user=user, algorithm=algorithm,
                                                                      work=previous_work, element=str(deleted_element))
                        saved_in_progress_element.delete()
                    except Http404:
                        pass

                for new_element in new_elements:
                    AlgorithmAdditionalElements.objects.create(
                        user=user,
                        algorithm=algorithm,
                        work=previous_work,
                        parent_element=get_object_or_404(Znanie, name=str(new_element['parent_element'])),
                        element_name=new_element['element_name'],
                        relation_type=new_element['relation_type'],
                        insertion_type=new_element['insertion_type'],
                    )

                for renamed_element in redacted_elements:
                    elem = get_object_or_404(AlgorithmAdditionalElements, user=user, algorithm=algorithm,
                                             work=previous_work, element_name=str(renamed_element[0]))
                    elem.element_name = renamed_element[1]
                    elem.save()

                return JsonResponse({}, status=200)

        raise Http404
