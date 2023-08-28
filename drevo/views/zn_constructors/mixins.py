from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.views.generic import CreateView

from drevo.models import SpecialPermissions


class DispatchMixin:
    """Миксин для проверки перед открытием страницы, является ли пользователь экспертом"""
    def dispatch(self, request, *args, **kwargs):
        expert = get_object_or_404(SpecialPermissions, expert=request.user)
        if not expert:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class FormKwargsMixin(LoginRequiredMixin, CreateView):
    """Миксин для избежания дублирования кода в нескольких классах"""
    def __init__(self):
        super().__init__()
        self.object = None
        self.type_of_zn = None

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['type_of_zn'] = self.type_of_zn
        return kwargs
