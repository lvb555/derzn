import copy
import json

from django.views.generic import TemplateView
from django.db import transaction, IntegrityError
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods

from drevo.models import RelationshipTzTr, Znanie, Tr, Relation, Tz, Author, KnowledgeStatuses
from drevo.relations_tree import get_descendants_for_knowledge
from drevo.forms.knowledge_create_form import ZnImageFormSet, ZnFilesFormSet
from drevo.forms.constructor_knowledge_form import MainZnInConstructorCreateEditForm, ZnForAlgorithmCreateUpdateForm
from drevo.utils.knowledge_tree_builder import KnowledgeTreeBuilder

from .mixins import DispatchMixin
from .supplementary_functions import create_relation, create_zn_for_constructor, get_images_from_request, \
    get_file_from_request


class AlgorithmConstructorView(DispatchMixin, TemplateView):
    """
    Отображение конструктора алгоритмов в виде дерева
    """
    # TODO Сделать это представление для всех конструкторов сложных знаний
    template_name = 'drevo/constructors/algorithm_constructor.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Конструктор алгоритмов'
        selected_zn_queryset = Znanie.objects.filter(id=self.kwargs.get('pk'))
        context['znanie'] = selected_zn_queryset
        selected_zn = selected_zn_queryset.first()
        context['main_zn_id'] = selected_zn.pk
        context['relative_znaniya'] = get_descendants_for_knowledge(selected_zn)

        main_zn_edit_form = MainZnInConstructorCreateEditForm(instance=selected_zn,
                                                              user=self.request.user,
                                                              type_of_zn='algorithm')

        context['main_zn_edit_form'] = main_zn_edit_form
        context['main_zn_edit_form_uuid'] = main_zn_edit_form.fields['content'].widget.attrs['id']

        context['images_form_for_main_zn'] = ZnImageFormSet(instance=selected_zn)
        context['file_form_for_main_zn'] = ZnFilesFormSet(instance=selected_zn)

        new_zn_form_create = ZnForAlgorithmCreateUpdateForm()
        context['new_zn_form_create'] = new_zn_form_create
        context['new_zn_form_create_uuid'] = new_zn_form_create.fields['content'].widget.attrs['id']

        new_zn_form_edit = ZnForAlgorithmCreateUpdateForm(tz_id=selected_zn.tz_id)
        context['new_zn_form_edit'] = new_zn_form_edit
        context['new_zn_form_edit_uuid'] = new_zn_form_edit.fields['content'].widget.attrs['id']

        context['images_form'] = ZnImageFormSet()
        context['file_form'] = ZnFilesFormSet()

        return context


@require_http_methods(['GET'])
def get_tr_for_create_relation_in_algorithm(request):
    """Получение допустимых видов связей для создания связи в алгоритме"""
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
    return JsonResponse(
        data={'bz': {'id': parent_id, 'name': get_object_or_404(Znanie, id=parent_id).name, 'editable': bz_editable},
              'relations': list(relations)}, status=200)


@require_http_methods(['GET'])
def get_tr_for_edit_relation_in_algorithm(request):
    """Получение допустимых видов связей для редактирования связи в алгоритме"""
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

    relations = (Tr.objects.filter(pk__in=[rel.rel_type_id for rel in relationships_with_parent_zn])
                 .values('id', 'name'))

    bz_editable = True if current_relation.bz.user_id == request.user.id else False
    rz_editable = True if get_object_or_404(Znanie, id=current_relation.rz_id).user_id == request.user.id else False

    return JsonResponse(data={
        'bz': {'id': parent_id, 'name': current_relation.bz.name, 'editable': bz_editable},
        'selected_tr': {'id': current_relation.tr_id, 'name': current_relation.tr.name},
        'selected_rz': {'id': base_kn_id, 'name': current_relation.rz.name, 'editable': rz_editable},
        'other_rz': list(other_rz_for_current_tr),
        'relations': list(relations),
        'rel_tz': [{'id': tz.get('id'), 'name': tz.get('name')} for tz in rel_tz]
    }, status=200)


@require_http_methods(['GET'])
def get_rel_zn_in_algorithm(request):
    """Получение допустимых видов связи и связанных знаний для создания связи в алгоритме"""
    bz_id = request.GET.get('bz_id')
    tr_id = request.GET.get('tr_id')
    base_knowledge_tz_id = get_object_or_404(Znanie, pk=bz_id).tz_id
    req_relationship = (
        RelationshipTzTr.objects
        .filter(Q(base_tz_id=base_knowledge_tz_id) & Q(rel_type_id=tr_id))
        .distinct()
    )
    rel_tz = Tz.objects.filter(pk__in=[rel.rel_tz_id for rel in req_relationship]).values('id', 'name')
    rel_zn = Znanie.objects.filter(tz__in=[rel.rel_tz_id for rel in req_relationship]).values('id', 'name')

    if not req_relationship:
        JsonResponse(data={})
    res_data = {'rel_zn': [{'id': zn.get('id'), 'name': zn.get('name')} for zn in rel_zn],
                'rel_tz': [{'id': tz.get('id'), 'name': tz.get('name')} for tz in rel_tz]}
    return JsonResponse(data=res_data)


@require_http_methods(['DELETE'])
@transaction.atomic
def delete_relation_in_algorithm(request):
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
def create_zn_in_algorithm(request):
    """Создание знания в алгоритме (с прикрепленными изображениями и файлом)"""
    req_data = request.POST
    form = ZnForAlgorithmCreateUpdateForm(data=req_data)
    images_form = ZnImageFormSet(req_data, get_images_from_request(request=request))
    file_form = ZnFilesFormSet(req_data, get_file_from_request(request=request))

    if form.is_valid() and images_form.is_valid() and file_form.is_valid():
        knowledge = form.save(commit=False)
        create_zn_for_constructor(knowledge, form, request, author=True, image_form=images_form, file_form=file_form)
        return JsonResponse(data={'zn_name': knowledge.name, 'zn_id': knowledge.id}, status=200)

    return JsonResponse(data={}, status=400)


@require_http_methods(['GET', 'POST'])
def edit_znanie_in_algorithm(request):
    """Редактирование атрибутов знания, прикрепленных изображений и файла в алгоритме"""
    if request.method == 'GET':
        u = ZnForAlgorithmCreateUpdateForm()
        znanie = get_object_or_404(Znanie, id=request.GET.get('zn_id'))
        form = ZnForAlgorithmCreateUpdateForm(instance=znanie, tz_id=znanie.tz_id)
        form_as_p = form.as_p()
        images_form = ZnImageFormSet(instance=znanie).as_p()
        file_form = ZnFilesFormSet(instance=znanie).as_p()
        return JsonResponse({
            'zn_name': form['name'].value(),
            'zn_tz': form['tz'].value(),
            'zn_content': form['content'].value(),
            'zn_href': form['href'].value(),
            'zn_source_com': form['source_com'].value(),
            'images_form': f"{images_form}",
            'file_form': f"{file_form}"
        }, status=200)
    else:
        req_data = request.POST
        existing_knowledge = get_object_or_404(Znanie, id=req_data.get('edited_zn_id'))
        form = ZnForAlgorithmCreateUpdateForm(data=req_data, instance=existing_knowledge)
        images_form = ZnImageFormSet(req_data, get_images_from_request(request=request), instance=existing_knowledge)
        file_form = ZnFilesFormSet(req_data, get_file_from_request(request=request), instance=existing_knowledge)

        if form.is_valid() and images_form.is_valid() and file_form.is_valid():
            knowledge = form.save(commit=False)
            create_zn_for_constructor(knowledge, form, request, image_form=images_form, file_form=file_form)
            return JsonResponse(data={'zn_id': knowledge.id, 'zn_name': knowledge.name}, status=200)
        return JsonResponse(data={}, status=400)


def delete_algorithm(request):
    """Удаление алгоритма: главного знания и всех связанных знаний"""
    main_zn = get_object_or_404(Znanie, id=request.GET.get('id'))
    rel_znaniya = get_descendants_for_knowledge(main_zn)
    for zn in rel_znaniya:
        zn.delete()
    main_zn.delete()
    return JsonResponse({'redirect_url': request.META['HTTP_REFERER']})


@require_http_methods(['GET'])
def is_current_user_creator_of_zn(request):
    """Проверка, является ли текущий пользователь создателем знания (для разрешения редактирования)"""
    zn_editable = True if get_object_or_404(Znanie, id=request.GET.get('id')).user_id == request.user.id else False
    return JsonResponse({'editable': zn_editable}, status=200)


@require_http_methods(['POST'])
@transaction.atomic
def save_rel_in_algorithm(request):
    """Сохранение новой/измененной связи в алгоритме"""
    rel_attrs = json.loads(request.body)
    bz_id = rel_attrs['bz_id']
    tr_id = rel_attrs['tr_id']
    rz_id = rel_attrs['rz_id']
    if rel_attrs['action'] == 'edit':
        Relation.objects.filter(bz_id=bz_id, tr_id=rel_attrs['last_tr_id'], rz_id=rel_attrs['last_rz_id']).delete()
    if not Relation.objects.filter(bz_id=bz_id, tr_id=tr_id, rz_id=rz_id, is_published=True).exists():
        create_relation(bz_id=bz_id, tr_id=tr_id, rz_id=rz_id, request=request)
    return JsonResponse({'redirect_url': request.META['HTTP_REFERER']})


@require_http_methods(['POST'])
def make_copy_of_algorithm(request):
    """Создание полной копии алгоритма со всеми знаниями и связями"""

    def copy_knowledge(knowledge: Znanie, author: Author, name: str = None, name_prefix: str = 'Копия - '):
        """
        Копирование знания \n
        knowledge: исходное знание; \n
        author: автор, который будет присвоен новому знанию; \n
        name: тема нового знания; \n
        name_prefix: если не передано name, в тему нового знания добавляется префикс. \n
        Возвращает новое знание
        """
        new_knowledge = copy.deepcopy(knowledge)
        if name:
            new_knowledge.name = name
        else:
            new_knowledge.name = f"{name_prefix}{new_knowledge.name}"
        new_knowledge.author = author
        new_knowledge.pk = None
        new_knowledge.id = None
        try:
            new_knowledge.save()
        except IntegrityError as e:
            return None
        return new_knowledge

    body = json.loads(request.body)
    id = body['id']
    name = body['name']
    user = request.user
    author, created = Author.objects.get_or_create(name=user.get_full_name())
    algorithm = Znanie.objects.get(id=id)
    descendants = get_descendants_for_knowledge(algorithm)
    tree_builder = KnowledgeTreeBuilder(
        queryset=descendants,
        show_complex=True,
    )

    copy_tree = {}
    new_znaniya = {}
    # Копия главного знания - алгоритма
    new_algorithm = copy_knowledge(algorithm, author, name)
    if not new_algorithm:
        return JsonResponse(data={}, status=409)
    KnowledgeStatuses.objects.create(
        knowledge=new_algorithm,
        status='PUB',
        user=request.user
    )

    new_znaniya[algorithm.id] = new_algorithm
    # Копирование связанных знаний исходного алгоритма
    for sm in tree_builder.relations_info:
        rel_zn = Relation.objects.get(id=tree_builder.relations_info[sm]['id'])

        if rel_zn.rz.id not in new_znaniya and rel_zn.rz in descendants:
            new_bz = copy_knowledge(rel_zn.rz, author)
            if not new_bz:
                return JsonResponse(data={}, status=409)
            new_znaniya[rel_zn.rz.id] = new_bz

        if rel_zn.bz.id not in copy_tree:
            copy_tree[rel_zn.bz.id] = {'type': rel_zn.tr, 'relations': []}

        copy_tree[rel_zn.bz.id]['relations'].append(rel_zn.rz.id)

    # Создание связей со скопированными знаниями
    for parent_zn in copy_tree:
        if parent_zn in new_znaniya:
            for child_zn in copy_tree[parent_zn]['relations']:
                Relation.objects.create(
                    bz=new_znaniya[parent_zn],
                    tr=copy_tree[parent_zn]['type'],
                    rz=new_znaniya[child_zn],
                    author=author,
                    user=user,
                    is_published=True
                )
    return JsonResponse({'id': new_algorithm.id})
