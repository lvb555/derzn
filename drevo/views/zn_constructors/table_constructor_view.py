import json

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.generic import TemplateView

from drevo.models import Znanie
from ...utils.knowledge_proxy import KnowledgeProxyError, TableProxy
from drevo.utils.common import get_user_roles, UserRoles
from .mixins import PrevNextMixin, DispatchMixin

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
        def get_permissions(roles):
            """ функция определяет права на редактирование таблицы исходя из ролей"""
            permissions = {
                'changeTable': 0,  # изменение структуры таблицы
                'changeTableText': 0,  # изменение заголовка таблицы
                'setValue': 0,  # изменение пустой ячейки
                'changeValue': 0,  # изменение заполненной ячейки
                'clearValue': 0,  # очистка ячейки
                'changeValueOwn': 0,  # изменение ячейки если я владелец
                'clearValueOwn': 0  # очистка ячейки если я владелец
            }

            if UserRoles.author in roles:
                permissions['changeTable'] = 1
                permissions['changeTableText'] = 1
                permissions['setValue'] = 1
                permissions['changeValue'] = 1
                permissions['clearValue'] = 1
                permissions['changeValueOwn'] = 1
                permissions['clearValueOwn'] = 1

            if UserRoles.expert in roles:
                permissions['setValue'] = 1
                permissions['clearValueOwn'] = 1
                permissions['changeValueOwn'] = 1

            if UserRoles.editor in roles:
                permissions['changeTable'] = 1
                permissions['changeTableText'] = 1
                permissions['setValue'] = 1
                permissions['changeValue'] = 1
                permissions['clearValue'] = 1
                permissions['changeValueOwn'] = 1
                permissions['clearValueOwn'] = 1

            if UserRoles.director in roles:
                permissions['changeTable'] = 1
                permissions['changeTableText'] = 1
                permissions['setValue'] = 1
                permissions['changeValue'] = 1
                permissions['clearValue'] = 1
                permissions['changeValueOwn'] = 1
                permissions['clearValueOwn'] = 1

            return permissions

        def get_user_level(roles):
            # определяем "уровень" пользователя от роли
            level = 0
            if UserRoles.author in roles:
                level = max(level, 0)
            if UserRoles.expert in roles:
                level = max(level, 0)
            if UserRoles.editor in roles:
                level = max(level, 1)
            if UserRoles.director in roles:
                level = max(level, 2)

            return level

        context = super().get_context_data(**kwargs)
        context["title"] = "Наполнение таблицы"

        object = Znanie.objects.get(id=self.kwargs["pk"])
        context["object"] = object

        table = TableProxy(object)
        header, cells = table.get_header_and_cells()
        user = self.request.user

        roles = get_user_roles(user, object)
        # print(roles)
        # print(object.user)
        # print([rol.name for rol in roles])

        context["table_data"] = cells
        context["table_header"] = header

        context["permissions"] = get_permissions(roles)
        context["permissions"]['changeTableText'] = 0
        context["user_level"] = get_user_level(roles)

        context["user_roles"] = [role.name for role in roles]
        context["user_roles_info"] = ', '.join([role.value for role in roles])

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
