from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import get_object_or_404

from drevo.models import SpecialPermissions


class DispatchMixin(AccessMixin):
    """Проверка перед открытием страницы, является ли пользователь экспертом"""
    def dispatch(self, request, *args, **kwargs):
        expert = get_object_or_404(SpecialPermissions, expert=request.user)
        if not expert:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)
