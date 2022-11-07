from django import template

from users.models import User

register = template.Library()


@register.filter(name='has_group')
def has_group(user: User, group_name: str) -> bool:
    return user.groups.filter(name=group_name).exists()
