from enum import Enum

from drevo.models import UserParameters, SettingsOptions, Znanie, SpecialPermissions, Category
from users.models import User


def validate_parameter_int(param: str | int | None, default: int = 0, good_values: list[int] | None = None) -> int:
    """ Валидация параметра param, который может быть числом, строкой или None
        Если передан список good_values - проверяется на вхождение в него
        Если параметр равен None - возвращается default
        Если параметр строка не является числом - возвращается default
        Если параметр не входит в список good_values - возвращается default
    """
    if param is None:
        return default

    if isinstance(param, str):
        if param.isnumeric():
            param = int(param)
        else:
            return default

    if good_values and param not in good_values:
        return default

    return param


def get_user_parameter(user: User, parameter_id: int) -> int | None:
    """ Ищет значение параметра пользователя по названию параметра
        Если такого параметра вообще нет - возвращает None
        Если у пользователя есть такой параметр - возвращает его значение
        Если у пользователя такого параметра нет (такого не может быть) - возвращает значение по умолчанию для параметра
    """
    # ищем по названию параметра
    option = SettingsOptions.objects.filter(pk=parameter_id).first()
    # если не находим - значит параметра такого нет
    if not option:
        return None

    param = UserParameters.objects.filter(user=user, param=option).first()
    if param:
        return param.param_value
    else:
        return option.default_param


class UserRoles(str, Enum):
    """
    Роли пользователя по отношению к конкретному знанию
    """
    author = 'Автор'
    expert = 'Эксперт'
    editor = 'Редактор'
    director = 'Руководитель'


def _check_categories_relationship(category_id: int, categories_ids: tuple) -> bool:
    """
    вспомогательная функция для проверки отношений между категориями
    """
    category = Category.objects.get(id=category_id)
    ancestor_ids = set(
        category.get_ancestors(include_self=True).values_list('id', flat=True)
    )
    return bool(ancestor_ids & set(categories_ids))


def get_user_roles(user: User, knowledge: Znanie) -> list[UserRoles]:
    """
    Возвращает роли пользователя относительно знания
    
    Args:
        user: Пользователь
        knowledge: Объект знания
        
    Returns:
        List[Roles]: Список ролей пользователя
        
    Note:
        Возможные роли: Автор, Эксперт, Редактор, Руководитель
    """
    roles = []

    # Проверка на авторство знания
    if knowledge.user == user:
        roles.append(UserRoles.author)

    # Быстрый выход, если у пользователя нет специальных прав
    if not any([user.is_expert, user.is_director, user.is_redactor]):
        return roles

    # Проверка категории знания
    knowledge_category = knowledge.category
    if not knowledge_category:
        return roles

    # Получение специальных прав с оптимизацией запросов
    permissions = (SpecialPermissions.objects
                   .prefetch_related('categories', 'admin_competencies')
                   .filter(expert=user)
                   .first())

    if not permissions:
        return roles

    # Получаем ID категорий один раз для оптимизации
    expert_categories_ids = tuple(
        permissions.categories.values_list('id', flat=True)
    )
    admin_categories_ids = tuple(
        permissions.admin_competencies.values_list('id', flat=True)
    )

    # Проверяем права эксперта
    if (any([user.is_expert, user.is_redactor])
            and expert_categories_ids
            and _check_categories_relationship(knowledge_category.id, expert_categories_ids)):

        if user.is_expert:
            roles.append(UserRoles.expert)
        if user.is_redactor:
            roles.append(UserRoles.editor)

    # Проверяем права руководителя
    if (user.is_director
            and admin_categories_ids
            and _check_categories_relationship(knowledge_category.id,admin_categories_ids)):
        roles.append(UserRoles.director)

    return roles
