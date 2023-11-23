from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from drevo.models import Znanie, Relation
from drevo.relations_tree import get_descendants_for_knowledge


def check_algorithm_correctness(algorithm_id):
    """
    Проверка корректности алгоритма.
    Используется атрибут «минимальное количество внутренних связей».
    В ходе проверки, если количество внутренних связей меньше минимального значения, выдается ошибка.
    Примечание: в ходе проверки никогда не учитываются связи вида «Далее».
    """
    algorithm = get_object_or_404(Znanie, id=algorithm_id)
    all_znaniya = [algorithm] + list(get_descendants_for_knowledge(algorithm))
    less_than_min = []
    for zn in all_znaniya:
        inner_rels_with_zn = Relation.objects.filter(bz=zn).exclude(tr__name='Далее')
        if inner_rels_with_zn.count() < zn.tz.min_number_of_inner_rels:
            less_than_min.append(f"{zn.tz.name} <{zn.name}>")
    if not less_than_min:
        return None
    return {'less_than_min': less_than_min}


@require_http_methods(['GET'])
def check_algorithm_correctness_from_request(request):
    """Проверка алгоритма с данными из GET-запроса"""
    algorithm_id = request.GET.get('id')
    check_algorithm = check_algorithm_correctness(algorithm_id)
    if check_algorithm is None:
        return JsonResponse({}, status=200)
    return JsonResponse(check_algorithm, status=200)
