def validate_parameter_int(param, default: int = 0, good_values: list = None):
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