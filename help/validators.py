from django.core.exceptions import ValidationError


def validate_tag(value):
    """
    Validator for the tag field:
    Checks that the string starts with '/'
    Does not end '/'
    """
    if value[0] != '/':
        raise ValidationError("Название тега должно начинаться с символа '/'",
                              params={'value': value},)
    if value[-1] == '/':
        raise ValidationError("Название тега должно быть без закрывающего '/' в конце",
                              params={'value': value},)
