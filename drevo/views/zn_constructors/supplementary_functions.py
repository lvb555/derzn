from django.db.models import QuerySet
from django.shortcuts import get_object_or_404

from drevo.models import Author, Relation, KnowledgeStatuses, Tr


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
        row_id = get_object_or_404(Tr, name='Строка').id
        column_id = get_object_or_404(Tr, name='Столбец').id
        if not (Relation.objects.filter(tr_id=row_id, bz_id=znanie.id, is_published=True).exists() and
                Relation.objects.filter(tr_id=column_id, bz_id=znanie.id, is_published=True).exists()):
            queryset = queryset.exclude(id=znanie.id)
    return queryset
