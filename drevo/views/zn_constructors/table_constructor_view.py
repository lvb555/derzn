import json

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.generic import TemplateView

from drevo.models import Znanie
from drevo.utils.knowledge_proxy import (
    KnowledgeProxyError,
    TableProxy,
    get_table_editor_permissions,
    get_user_editor_level,
    get_user_roles,
)

from .mixins import DispatchMixin, PrevNextMixin

"""
 #####################################################################

 View конструктора таблиц и наполнения таблиц

 #####################################################################
"""


class TableFillingView(LoginRequiredMixin, DispatchMixin, PrevNextMixin, TemplateView):
    """Представление для страницы «Наполнение таблицы»"""

    template_name = "drevo/constructors/table_editor.html"
    ok_message = "Изменения в таблице успешно сохранены!"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Наполнение таблицы"

        object = Znanie.objects.get(id=self.kwargs["pk"])
        context["object"] = object

        table = TableProxy(object)
        header, cells = table.get_header_and_cells()
        user = self.request.user

        roles = get_user_roles(user, object)

        context["table_data"] = cells
        context["table_header"] = header
        context["permissions"] = get_table_editor_permissions(roles)
        context["user_level"] = get_user_editor_level(roles)
        context["user_roles_info"] = ", ".join([role.value for role in roles])

        return context

    def form_invalid(self):
        return self.get(self.request)

    def post(self, request, *args, **kwargs):

        # если пришли данные не json - ничего не делаем
        if not request.accepts("application/json"):
            messages.warning(request, "Неверный формат запроса")
            return self.form_invalid()

        knowledge = Znanie.objects.get(id=kwargs["pk"])
        table = TableProxy(knowledge)
        table_data = json.loads(self.request.body)
        try:
            table.update_table(table_data, self.request.user)

        except KnowledgeProxyError as e:
            return JsonResponse({"result": str(e)}, status=409)

        return JsonResponse({"result": self.ok_message}, status=200)
