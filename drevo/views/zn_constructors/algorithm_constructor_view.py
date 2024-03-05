from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from drevo.models import Znanie

from ...relations_tree import get_descendants_for_knowledge


def delete_algorithm(request):
    """Удаление алгоритма: главного знания и всех связанных знаний, не являющихся алгоритмом"""
    main_zn = get_object_or_404(Znanie, id=request.GET.get('id'))
    rel_znaniya = get_descendants_for_knowledge(main_zn)
    for zn in rel_znaniya:
        if zn.tz.name != 'Алгоритм':
            zn.delete()
    main_zn.delete()
    return HttpResponse(status=200)
