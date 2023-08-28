from drevo.models import Author, Relation, KnowledgeStatuses


def create_relation(bz_id, rz_id, tr_id, request, order_of_relation=None, is_answer=False):
    """Создание опубликованной связи с заданными параметрами"""

    # Создание автора с именем и фамилией пользователя, если такого не существует
    author, created = Author.objects.get_or_create(
        name=f"{request.user.first_name} {request.user.last_name}",
    )

    if is_answer:
        # Проверка на уже существующую связь и изменение ее вида связи
        # (например, изменить "Ответ верный" на "Ответ неверный")
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


def create_zn_for_constructor(knowledge, form, request, tz_id=None, author=True, image_form=None):
    """Функция для создания атрибутов нового знания"""
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
