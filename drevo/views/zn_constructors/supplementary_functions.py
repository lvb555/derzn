import copy
import json

from django.db.models import QuerySet
from django.shortcuts import get_object_or_404

from django.db import IntegrityError
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from drevo.models import Znanie, Relation, Author, KnowledgeStatuses, Tr, Tz
from drevo.relations_tree import get_descendants_for_knowledge
from drevo.utils.knowledge_tree_builder import KnowledgeTreeBuilder


def create_relation(bz_id, rz_id, tr_id, request, order_of_relation=None, is_answer=False):
    """Создание опубликованной связи с заданными параметрами"""

    # Создание автора с именем и фамилией пользователя, если такого не существует
    author, created = Author.objects.get_or_create(
        name=f"{request.user.first_name} {request.user.last_name}",
    )
    relation = None
    if is_answer:
        # Проверка на уже существующую связь и изменение ее вида связи
        # (чтобы изменить "Ответ верный" на "Ответ неверный" и наоборот)
        relation = Relation.objects.filter(
            bz_id=bz_id,
            rz_id=rz_id,
            author_id=author.id,
            is_published=True,
        ).first()
        if relation:
            relation.tr_id = tr_id
    if not relation:
        # Создание опубликованной связи с выбранными значениями, если оно не было создано
        relation, created = Relation.objects.get_or_create(
            bz_id=bz_id,
            tr_id=tr_id,
            rz_id=rz_id,
            author_id=author.id,
            is_published=True,
            defaults={'user_id': request.user.id}
        )

    if order_of_relation:
        relation.order = order_of_relation
    relation.save()


def create_zn_for_constructor(knowledge, form, request, tz_id=None, author=True, image_form=None, file_form=None):
    """Функция для создания нового знания"""
    if tz_id:
        knowledge.tz_id = tz_id
    if author:
        author, created = Author.objects.get_or_create(
            name=f"{request.user.first_name} {request.user.last_name}",
        )
        knowledge.author_id = author.id
    knowledge.is_published = True
    knowledge.user = request.user
    # Сохраняем Знание
    knowledge.save()
    form.save_m2m()
    # Создание записи
    KnowledgeStatuses.objects.create(
        knowledge=knowledge,
        status='PUB',
        user=request.user
    )
    if image_form:
        # Перед сохранением формы с изображениями подставляем текущий объект знания
        image_form.instance = knowledge
        image_form.save()
    if file_form:
        # Перед сохранением формы с файлом подставляем текущий объект знания
        file_form.instance = knowledge
        file_form.save()


def get_images_from_request(request):
    """Получение файлов из формы с изображениями (при условии, что в форме 3 изображения)"""
    images_form_data = {}
    for i in range(0, 3):
        field_name = f"photos-{i}-photo"
        if field_name in request.FILES:
            images_form_data[field_name] = request.FILES[field_name]
    return images_form_data


def get_file_from_request(request):
    """Получение файла из формы с файлом (при условии, что в форме 1 файл)"""
    file_form_data = {}
    field_name = f"files-0-file"
    if field_name in request.FILES:
        file_form_data[field_name] = request.FILES[field_name]
    return file_form_data


def delete_tables_without_row_and_columns(queryset: QuerySet) -> QuerySet:
    """Удаляет из queryset таблицы, не содержащие строки и столбцы"""
    for znanie in queryset:
        group_kind = get_object_or_404(Tz, name='Группа').id
        structure_kind = get_object_or_404(Tr, name='Состав').id

        row_id = get_object_or_404(Tr, name='Строка').id
        column_id = get_object_or_404(Tr, name='Столбец').id

        # Удаляются таблицы, в которых нет хотя бы одной строки и столбца
        if not (Relation.objects.filter(tr_id=row_id, bz_id=znanie.id, is_published=True).exists() and
                Relation.objects.filter(tr_id=column_id, bz_id=znanie.id, is_published=True).exists()):
            queryset = queryset.exclude(id=znanie.id)

        # Удаляются таблицы, строки которых - группы, при этом нет хотя бы одного элемента строки
        relation_row_group = Relation.objects.filter(bz_id=znanie.id, rz__tz_id=group_kind, tr__name="Строка",
                                                     is_published=True).first()
        if relation_row_group:
            if not Relation.objects.filter(bz_id=relation_row_group.rz_id, tr_id=structure_kind,
                                           is_published=True).exists():
                queryset = queryset.exclude(id=znanie.id)

        # Удаляются таблицы, столбцы которых - группы, при этом нет хотя бы одного элемента столбца
        relation_column_group = Relation.objects.filter(bz_id=znanie.id, rz__tz_id=group_kind, tr__name="Столбец",
                                                        is_published=True).first()
        if relation_column_group:
            if not Relation.objects.filter(bz_id=relation_column_group.rz_id, tr_id=structure_kind,
                                           is_published=True).exists():
                queryset = queryset.exclude(id=znanie.id)
    return queryset


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
