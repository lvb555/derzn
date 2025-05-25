from django import template
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from drevo.models.knowledge import Znanie
from drevo.models.knowledge_kind import Tz
from drevo.utils.knowledge_proxy import TableProxy

register = template.Library()

"""
   тег для рендера в HTML разных типов знаний
   для того, чтобы не плодить портянки с кучей if .. elif ...
   использование:
   {% load render_knowledge %}
   {% render_knowledge knowledge val_1=... val_2=... %}
   для вызываемого типа должно быть реализован свой рендер!
   Реализуется просто - надо создать класс от KnowledgeRender
   и переопределить методы __init__() и render()
   см. реализацию для Таблицы ниже"""


@register.simple_tag
def render_knowledge(knowledge: Znanie, **kwargs):
    return KnowledgeRender.get_render(knowledge, **kwargs)


class KnowledgeRender:
    """
    Родительский объект для классов рендера Знания
    KnowledgeRender.get_render(knowledge) вернет представление HTML для
    переданного типа Знание (например Таблица) либо вернет результат из empty_result
    если не реализован потомок для данного типа
    """

    renders = None

    def __init__(self, knowledge_type: Tz, template_name: str):
        self.knowledge_type = knowledge_type
        self.template_name = template_name

    @staticmethod
    def show_message(message: str):
        result = f'<div class="render_message"><p>{message}</p></div>'
        return mark_safe(result)

    @staticmethod
    def empty_result(name: str):
        return KnowledgeRender.show_message(
            f"Отображение для Знание {name} не реализовано"
        )

    def render(self, knowledge: Znanie, **kwargs):
        # этот метод должен быть реализован в потомках!
        raise NotImplementedError

    @classmethod
    def get_render(cls, knowledge: Znanie, **kwargs):
        knowledge_type = knowledge.tz
        if cls.renders is None:
            cls.renders = {}
            for render_class in cls.__subclasses__():
                render = render_class()
                cls.renders[render.knowledge_type] = render
        render_for_knowledge = cls.renders.get(knowledge_type)
        if render_for_knowledge:
            return render_for_knowledge.render(knowledge, **kwargs)
        else:
            return cls.empty_result(knowledge.name)


class TableRender(KnowledgeRender):
    """
    Рендер для типа Таблицы
    использование {% render_knowledge object table_id='table_1' %}
    table_id - это id блока div с таблицей - если надо их разделить
    """

    def __init__(self):
        table_type = Tz.t_("Таблица")
        template_name = "drevo/tags/render_knowledge/table.html"
        super().__init__(table_type, template_name)

    def render(self, knowledge: Znanie, **kwargs):
        if knowledge.tz != self.knowledge_type:
            return self.show_message(f"{knowledge} ! не таблица!")

        header, values = TableProxy(knowledge).get_render_data()

        group = header.get("group", None)
        group_col = header.get("group_col", None)
        group_row = header.get("group_row", None)

        cols = list(map(lambda x: x["name"], header.get("cols", [])))
        rows = list(map(lambda x: x["name"], header.get("rows", [])))

        if not (cols and rows):
            return self.show_message("[Пустая таблица]")
        context = {
            "group": group,
            "group_col": group_col,
            "group_row": group_row,
            "cols": cols,
            "rows": rows,
            "values": values,
            "table_id": kwargs.get("table_id", "table_1"),
        }

        return render_to_string(self.template_name, context)
