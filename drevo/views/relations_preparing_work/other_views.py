from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q, Count, Case, When, IntegerField
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_http_methods

from drevo.models import Znanie, RelationshipTzTr, Tz, Relation


@require_http_methods(['GET'])
def check_related(request):
    """
        Эндпоинт для проверки связанного знания при создании связи
    """
    rz_pk = request.GET.get('rz_id')
    knowledge = (
        Znanie.objects
        .select_related('user')
        .filter(pk=rz_pk)
        .annotate(
            is_pub=Case(
                When(knowledge_status__status='PUB_PRE', then=1),
                When(knowledge_status__status='PUB', then=1),
                default=0,
                output_field=IntegerField()
            ),
            user_kn=Case(
                When(
                    Q(user_id=request.user.pk) & (
                            Q(knowledge_status__status='WORK_PRE') | Q(knowledge_status__status='WORK')
                    ), then=1),
                    # When(user__is_expert=True, then=1),
                    # When(user__is_director=True, then=1),
                default=0,
                output_field=IntegerField()
            ),
        )
        .first()
    )

    res_data = {'user_knowledge': False, 'is_pub': False}
    if not knowledge:
        return JsonResponse(data=res_data)

    if knowledge.user_kn:
        res_data['user_knowledge'] = True
    if knowledge.is_pub:
        res_data['is_pub'] = True
    return JsonResponse(data=res_data)


@require_http_methods(['GET'])
def get_related_tz(request):
    """
        Эндпоинт для получения допустимых видов знаний для создания дополнительных знаний
    """
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
        related_tz = Tz.objects.filter(is_systemic=False).values('id', 'name')
    else:
        related_tz = Tz.objects.filter(pk__in=req_relationship, is_systemic=False).values('id', 'name').distinct()
    res_data = {'related_tz': [{'id': tz.get('id'), 'name': tz.get('name')} for tz in related_tz]}
    return JsonResponse(data=res_data)


@login_required
@require_http_methods(['GET'])
@transaction.atomic
def relation_delete_view(request):
    """
        Вьюшка удаления связи
    """
    bz = request.GET.get('bz_id')
    rz = request.GET.get('rz_id')
    Relation.objects.filter(bz_id=bz, rz_id=rz, user=request.user).delete()
    return redirect(request.META['HTTP_REFERER'])
