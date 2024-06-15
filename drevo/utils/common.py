from drevo.models import UserParameters, SettingsOptions
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

