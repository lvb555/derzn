from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import get_object_or_404, redirect

from drevo.models import SpecialPermissions


class DispatchMixin(AccessMixin):
    """Проверка перед открытием страницы, является ли пользователь экспертом"""
    def dispatch(self, request, *args, **kwargs):
        expert = get_object_or_404(SpecialPermissions, expert=request.user)
        if not expert:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class PrevNextMixin:
    """
    Миксин добавляет обработку параметров prev и next
    prev - ссылка на предыдущую страницу (откуда пришли) либо явно заданная ссылка
    next - явно заданная ссылка на следующую страницу
    в шаблоне надо соответственно сохранить эти параметры как hidden
        <input type="hidden" name="prev" id="prev" value="{{ prev }}">
        <input type="hidden" name="next" id="next" value="{{ next }}">
    Логика работы (в form_valid()):
    1. если был задан параметр next - перенаправляем на эту страницу
    2. если есть параметр prev - перенаправляем на страницу prev (только если там не корень)
    3. если нет никаких параметров - перенаправляем на свою же страницу - надо обдумать)


    Нужен чтобы кнопка Назад работала правильно
    Так же добавляется поддержка параметра next - перенаправление на другую страницу после успешного сохранения
    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # берем поле prev из POST, если его там нет - из HTTP_REFERER
        # по этому полю будем уходить по кнопке «Назад»
        if self.request.GET.get("next"):
            context["next"] = self.request.GET.get("next")

        if self.request.GET.get("prev"):
            context["prev"] = self.request.GET.get("prev")

        elif self.request.POST.get("prev"):
            context["prev"] = self.request.POST.get("prev")

        elif self.request.META.get("HTTP_REFERER"):
            context["prev"] = self.request.META.get("HTTP_REFERER")
        else:
            # если же пришли из ниоткуда - при закрытии уходим на главную страницу
            # upd: не уходим, а остаемся на этой странице
            context["prev"] = "/"
        return context

    def form_valid(self):
        # если есть параметр next - уходим по нему
        # если нет - уходим по prev (только если там не корень)
        # если и его нет - уходим обратно на эту же страницу

        if self.request.POST.get("next"):
            return redirect(self.request.POST.get("next"))

        context = self.get_context_data()

        if "prev" in context:
            if context["prev"] != "/":
                return redirect(context["prev"])

        # если не было prev и next - остаемся на этой странице
        return self.get(self.request)
