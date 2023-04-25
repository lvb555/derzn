from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from ..models import RelationshipTzTr, Znanie, Tr
from django.views.decorators.http import require_http_methods


@require_http_methods(['GET'])
def get_required_tr(request):
    bz_id = request.GET.get('bz_id')

    base_knowledge_tz = get_object_or_404(Znanie, pk=bz_id).tz_id
    req_relationship = (
        RelationshipTzTr.objects
        .filter(Q(base_tz_id=base_knowledge_tz) | Q(base_tz=None))
        .values_list('rel_type', flat=True)
        .distinct()
    )

    if not req_relationship:
        return JsonResponse(data={})

    if None in req_relationship:
        relation_types = Tr.objects.values('id', 'name')
        res_data = {'required_tr': [{'id': tr.get('id'), 'name': tr.get('name')} for tr in relation_types]}
        return JsonResponse(data=res_data)

    relation_types = Tr.objects.filter(pk__in=req_relationship).values('id', 'name').distinct()
    res_data = {'required_tr': [{'id': tr.get('id'), 'name': tr.get('name')} for tr in relation_types]}
    return JsonResponse(data=res_data)


@require_http_methods(['GET'])
def get_required_rz(request):
    bz_id = request.GET.get('bz_id')
    tr_id = request.GET.get('tr_id')

    base_knowledge_tz = get_object_or_404(Znanie, pk=bz_id).tz_id
    req_relationship = (
        RelationshipTzTr.objects
        .filter((Q(base_tz_id=base_knowledge_tz) | Q(base_tz=None)) & (Q(rel_type_id=tr_id) | Q(rel_type=None)))
        .values_list('rel_tz', flat=True)
        .distinct()
    )

    if not req_relationship:
        JsonResponse(data={})

    if None in req_relationship:
        related_knowledge = Znanie.objects.values('id', 'name')
        res_data = {'required_rz': [{'id': rz.get('id'), 'name': rz.get('name')} for rz in related_knowledge]}
        return JsonResponse(data=res_data)

    related_knowledge = Znanie.objects.filter(tz_id__in=req_relationship).values('id', 'name').distinct()
    res_data = {'required_rz': [{'id': rz.get('id'), 'name': rz.get('name')} for rz in related_knowledge]}
    return JsonResponse(data=res_data)
