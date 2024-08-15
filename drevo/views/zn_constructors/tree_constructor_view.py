import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import TemplateView
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods

from drevo.models import RelationshipTzTr, Znanie, Tr, Relation, Tz
from drevo.relations_tree import get_descendants_for_knowledge
from drevo.forms.knowledge_create_form import ZnImageFormSet, ZnFilesFormSet
from drevo.forms.constructor_knowledge_form import MainZnInConstructorCreateEditForm, \
    ZnForTreeConstructorCreateUpdateForm

from .mixins import DispatchMixin
from .supplementary_functions import create_relation, create_zn_for_constructor, get_images_from_request, \
    get_file_from_request
from ..algorithm_detail_view import make_complicated_dict1


# --------------------------------------------------------------
# Views для конструктора знаний, который строится в виде дерева
# (на данный момент Конструктор алгоритмов и документов)
# --------------------------------------------------------------


def get_rel_zn_in_tree_constructor(bz_id, tr_id):
    """Получение допустимых видов связи и связанных знаний для создания связи в древовидном конструкторе"""
    base_knowledge_tz_id = get_object_or_404(Znanie, pk=bz_id).tz_id
    req_relationship = (
        RelationshipTzTr.objects
        .filter(Q(base_tz_id=base_knowledge_tz_id) & Q(rel_type_id=tr_id))
        .distinct()
    )
    rel_tz = Tz.objects.filter(pk__in=[rel.rel_tz_id for rel in req_relationship]).values('id', 'name')
    rel_zn = Znanie.objects.filter(tz__in=[rel.rel_tz_id for rel in req_relationship]).values('id', 'name')
    return req_relationship, rel_tz, rel_zn


class TreeConstructorView(LoginRequiredMixin, DispatchMixin, TemplateView):
    """Отображение древовидного конструктора"""
    template_name = 'drevo/constructors/tree_constructor.html'

    def get(self, request, *args, **kwargs):
        type_of_zn = self.kwargs.get('type')
        selected_zn = Znanie.objects.filter(id=self.kwargs.get('pk')).first()
        if (type_of_zn == 'algorithm' and selected_zn.tz.name != 'Алгоритм') or (type_of_zn == 'document' and
                                                                                 selected_zn.tz.name != 'Документ') \
                or (type_of_zn == 'discussion' and
                    selected_zn.tz.name != 'Дискуссии'):
            return HttpResponseRedirect(reverse('drevo'))

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        type_of_zn = self.kwargs.get('type')
        selected_zn_queryset = Znanie.objects.filter(id=self.kwargs.get('pk'))
        context['znanie'] = selected_zn_queryset
        selected_zn = selected_zn_queryset.first()
        context['type_of_zn'] = self.kwargs.get('type')
        context['main_zn_id'] = selected_zn.pk
        if type_of_zn == 'algorithm':
            context['title'] = 'Конструктор алгоритма'
            try:
                next_relation = Tr.objects.get(name='Далее')
            except Tr.DoesNotExist:
                next_relation = None
            try:
                start_of_algorithm = Relation.objects.get(bz=selected_zn, tr__name='Начало алгоритма').rz
                context['relative_znaniya'] = make_complicated_dict1(
                    {'previous_key': []},
                    start_of_algorithm,
                    'previous_key',
                    next_relation=next_relation
                )['previous_key']
            except Relation.DoesNotExist:
                context['relative_znaniya'] = []
        else:
            context['title'] = 'Конструктор документа' or "Дискуссии для экспертов"
            context['relative_znaniya'] = get_descendants_for_knowledge(selected_zn)

        main_zn_edit_form = MainZnInConstructorCreateEditForm(instance=selected_zn,
                                                              user=self.request.user,
                                                              type_of_zn=type_of_zn)
        context['main_zn_edit_form'] = main_zn_edit_form
        context['main_zn_edit_form_uuid'] = main_zn_edit_form.fields['content'].widget.attrs['id']

        context['images_form_for_main_zn'] = ZnImageFormSet(instance=selected_zn)
        context['file_form_for_main_zn'] = ZnFilesFormSet(instance=selected_zn)

        new_zn_form_create = ZnForTreeConstructorCreateUpdateForm()
        context['new_zn_form_create'] = new_zn_form_create
        context['new_zn_form_create_uuid'] = new_zn_form_create.fields['content'].widget.attrs['id']

        new_zn_form_edit = ZnForTreeConstructorCreateUpdateForm(tz_id=selected_zn.tz_id)
        context['new_zn_form_edit'] = new_zn_form_edit
        context['new_zn_form_edit_uuid'] = new_zn_form_edit.fields['content'].widget.attrs['id']

        context['images_form'] = ZnImageFormSet()
        context['file_form'] = ZnFilesFormSet()

        return context




@require_http_methods(['GET'])
def get_tr_for_create_relation_in_tree_constructor(request):
    """Получение допустимых видов связей для создания связи в древовидном конструкторе"""
    parent_id = request.GET.get('parent_id')

    parent_zn = get_object_or_404(Znanie, id=parent_id)
    relationships_with_parent_zn = RelationshipTzTr.objects.filter(base_tz_id=parent_zn.tz_id)

    existing_relations = Relation.objects.filter(bz_id=parent_id).distinct().exclude(tr__name='Далее')
    # Для условия с уже созданной связью "Тогда"/"Иначе" возможно только создание связи "Иначе"/"Тогда"
    if parent_zn.tz.name == 'Условие' and existing_relations.count() == 1:
        if existing_relations.first().tr.name == 'Тогда':
            relationships_with_parent_zn = relationships_with_parent_zn.exclude(rel_type__name='Тогда')
        else:
            relationships_with_parent_zn = relationships_with_parent_zn.exclude(rel_type__name='Иначе')

    relations = (Tr.objects.filter(pk__in=[rel.rel_type_id for rel in relationships_with_parent_zn])
                 .values('id', 'name'))
    bz_editable = True if parent_zn.user_id == request.user.id else False
    if relations.count() == 1:
        tr_id = relations.first()['id']
        req_relationship, rel_tz, rel_zn = get_rel_zn_in_tree_constructor(parent_id, tr_id)
        if req_relationship:
            return JsonResponse(
                data={'bz': {'id': parent_id,
                             'name': get_object_or_404(Znanie, id=parent_id).name,
                             'editable': bz_editable},
                      'relations': list(relations),
                      'rel_zn': [{'id': zn.get('id'), 'name': zn.get('name')} for zn in rel_zn],
                      'rel_tz': [{'id': tz.get('id'), 'name': tz.get('name')} for tz in rel_tz]},
                status=200)

    return JsonResponse(
        data={'bz': {'id': parent_id, 'name': get_object_or_404(Znanie, id=parent_id).name, 'editable': bz_editable},
              'relations': list(relations)}, status=200)


@require_http_methods(['GET'])
def get_tr_for_edit_relation_in_tree_constructor(request):
    """Получение допустимых видов связей для редактирования связи в древовидном конструкторе"""
    current_relation = get_object_or_404(Relation, pk=request.GET.get('rel_id'))
    parent_id = current_relation.bz_id
    base_kn_id = current_relation.rz_id

    parent_zn = get_object_or_404(Znanie, id=parent_id)
    relationships_with_parent_zn = (RelationshipTzTr.objects
                                    .filter(base_tz_id=parent_zn.tz_id))
    child_relationships = Relation.objects.filter(bz_id=base_kn_id).values('tr_id', 'rz__tz')
    existing_relations = Relation.objects.filter(bz_id=parent_id).distinct().exclude(tr__name='Далее')

    # Для редактирования связи с базовым знанием вида "Условие" исключается возможность создать 2 связи "Тогда"/"Иначе"
    if existing_relations.count() == 2 and current_relation.tr.name == 'Тогда':
        relationships_with_parent_zn = relationships_with_parent_zn.exclude(rel_type__name='Иначе')
    elif existing_relations.count() == 2 and current_relation.tr.name == 'Иначе':
        relationships_with_parent_zn = relationships_with_parent_zn.exclude(rel_type__name='Тогда')

    for relationship in relationships_with_parent_zn:
        # Если одну из дочерних связей нельзя связать с текущим видом знания, то он удаляется
        for child_relationship in child_relationships:
            if not RelationshipTzTr.objects.filter(base_tz_id=relationship.rel_tz_id,
                                                   rel_type_id=child_relationship['tr_id'],
                                                   rel_tz_id=child_relationship['rz__tz']).exists():
                relationships_with_parent_zn = relationships_with_parent_zn.exclude(pk=relationship.pk)
                continue

    rel_tz = Tz.objects.filter(pk__in=[rel.rel_tz_id for rel in relationships_with_parent_zn]).values('id', 'name')

    relationships_with_parent_zn = relationships_with_parent_zn.exclude(base_tz_id=current_relation.bz.tz_id,
                                                                        rel_type_id=current_relation.tr_id,
                                                                        rel_tz_id=current_relation.rz.tz_id)
    other_rz_for_current_tr = (Znanie.objects.filter(tz_id=current_relation.rz.tz_id)
                               .exclude(pk=base_kn_id)
                               .values('id', 'name')
                               )

    other_tr = (Tr.objects.filter(pk__in=[rel.rel_type_id for rel in relationships_with_parent_zn])
                .values('id', 'name'))

    bz_editable = True if current_relation.bz.user_id == request.user.id else False
    rz_editable = True if get_object_or_404(Znanie, id=current_relation.rz_id).user_id == request.user.id else False

    return JsonResponse(data={
        'bz': {'id': parent_id, 'name': current_relation.bz.name, 'editable': bz_editable},
        'selected_tr': {'id': current_relation.tr_id, 'name': current_relation.tr.name},
        'selected_rz': {'id': base_kn_id, 'name': current_relation.rz.name, 'editable': rz_editable},
        'selected_order': {'id': current_relation.order},
        'other_rz': list(other_rz_for_current_tr),
        'other_tr': list(other_tr),
        'rel_tz': [{'id': tz.get('id'), 'name': tz.get('name')} for tz in rel_tz]
    }, status=200)


@require_http_methods(['GET'])
def get_rel_zn_in_tree_constructor_from_request(request):
    bz_id = request.GET.get('bz_id')
    tr_id = request.GET.get('tr_id')
    req_relationship, rel_tz, rel_zn = get_rel_zn_in_tree_constructor(bz_id, tr_id)
    if not req_relationship:
        JsonResponse(data={})
    res_data = {'rel_zn': [{'id': zn.get('id'), 'name': zn.get('name')} for zn in rel_zn],
                'rel_tz': [{'id': tz.get('id'), 'name': tz.get('name')} for tz in rel_tz]}
    return JsonResponse(data=res_data)


@require_http_methods(['DELETE'])
@transaction.atomic
def delete_relation_in_tree_constructor(request):
    """Удаление текущей и дочерних связей"""
    rel_zn_id = request.GET.get('rz_id')
    Relation.objects.filter(bz_id=request.GET.get('bz_id'), rz_id=rel_zn_id).delete()
    zn = get_object_or_404(Znanie, id=rel_zn_id)
    child_for_rel_zn = get_descendants_for_knowledge(zn)
    for zn in child_for_rel_zn:
        Relation.objects.filter(rz_id=zn).delete()
    return JsonResponse({'redirect_url': request.META['HTTP_REFERER']})


@require_http_methods(['POST'])
@transaction.atomic
def create_zn_in_tree_constructor(request):
    """Создание знания в древовидном конструкторе (с прикрепленными изображениями и файлом)"""
    req_data = request.POST
    form = ZnForTreeConstructorCreateUpdateForm(data=req_data)
    images_form = ZnImageFormSet(req_data, get_images_from_request(request=request))
    file_form = ZnFilesFormSet(req_data, get_file_from_request(request=request))

    if form.is_valid() and images_form.is_valid() and file_form.is_valid():
        knowledge = form.save(commit=False)
        create_zn_for_constructor(knowledge, form, request, author=True, image_form=images_form, file_form=file_form)
        return JsonResponse(data={'zn_name': knowledge.name, 'zn_id': knowledge.id}, status=200)

    return JsonResponse(data={}, status=400)


@require_http_methods(['GET'])
def is_current_user_creator_of_zn(request):
    """Проверка, является ли текущий пользователь создателем знания (для разрешения редактирования)"""
    zn_editable = True if get_object_or_404(Znanie, id=request.GET.get('id')).user_id == request.user.id else False
    return JsonResponse({'editable': zn_editable}, status=200)


@require_http_methods(['GET'])
def get_order_of_relation(request):
    """Получение порядкового номера связи (который является необязательным атрибутом)"""
    rel = Relation.objects.filter(bz_id=request.GET.get('bz_id'), tr_id=request.GET.get('tr_id'),
                                  rz_id=request.GET.get('rz_id')).first()
    if rel:
        order = rel.order
        return JsonResponse({'order': order}, status=200)

    return JsonResponse({}, status=200)


@require_http_methods(['GET', 'POST'])
def edit_znanie_in_tree_constructor(request):
    """Редактирование атрибутов знания, прикрепленных изображений и файла в древовидном конструкторе"""
    if request.method == 'GET':
        znanie = get_object_or_404(Znanie, id=request.GET.get('zn_id'))
        form = ZnForTreeConstructorCreateUpdateForm(instance=znanie, tz_id=znanie.tz_id)
        images_form = ZnImageFormSet(instance=znanie).as_p()
        file_form = ZnFilesFormSet(instance=znanie).as_p()
        return JsonResponse({
            'zn_name': form['name'].value(),
            'zn_tz': znanie.tz.name,
            'zn_content': form['content'].value(),
            'zn_href': form['href'].value(),
            'zn_source_com': form['source_com'].value(),
            'images_form': f"{images_form}",
            'file_form': f"{file_form}"
        }, status=200)
    else:
        req_data = request.POST
        existing_knowledge = get_object_or_404(Znanie, id=req_data.get('edited_zn_id'))
        form = ZnForTreeConstructorCreateUpdateForm(data=req_data, instance=existing_knowledge)
        images_form = ZnImageFormSet(req_data, get_images_from_request(request=request), instance=existing_knowledge)
        file_form = ZnFilesFormSet(req_data, get_file_from_request(request=request), instance=existing_knowledge)

        if form.is_valid() and images_form.is_valid() and file_form.is_valid():
            knowledge = form.save(commit=False)
            create_zn_for_constructor(knowledge, form, request, image_form=images_form, file_form=file_form)
            return JsonResponse(data={'zn_id': knowledge.id, 'zn_name': knowledge.name}, status=200)
        return JsonResponse(data={}, status=400)


@require_http_methods(['POST'])
@transaction.atomic
def save_rel_in_tree_constructor(request):
    """Сохранение новой/измененной и удаление прошлой связи в древовидном конструкторе"""
    rel_attrs = json.loads(request.body)
    bz_id = rel_attrs['bz_id']
    tr_id = rel_attrs['tr_id']
    rz_id = rel_attrs['rz_id']
    order = rel_attrs['order']
    if rel_attrs['action'] == 'edit':
        last_tr_id = rel_attrs['last_tr_id']
        last_rz_id = rel_attrs['last_rz_id']
        if not (tr_id == last_tr_id and rz_id == last_rz_id):
            Relation.objects.filter(bz_id=bz_id, tr_id=last_tr_id, rz_id=last_rz_id).delete()
    create_relation(bz_id=bz_id, tr_id=tr_id, rz_id=rz_id, user=request.user, order_of_relation=order)
    return JsonResponse({'redirect_url': request.META['HTTP_REFERER']})
