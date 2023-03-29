from django.core.exceptions import EmptyResultSet
from django.db.models import QuerySet
from django.template import Library
from django.utils.safestring import mark_safe
from drevo.utils.knowledge_tree_builder import KnowledgeTreeBuilder
from drevo.models import Znanie, Category, Tr, Author

register = Library()


@register.inclusion_tag('drevo/tags/knowledge_tree.html')
def build_knowledge_tree(queryset: QuerySet[Znanie],
                         tree_num: int = 1,
                         empty_tree_message: str = '',
                         show_only: Tr = None,
                         hidden_author: Author = None,
                         show_complex: bool = False
                         ):
    """
        Тег для построения дерева знаний \n
        tree_num: номер дерева (на случай если необходимо на одной странице создать несколько деревьев); \n

        empty_tree_message: если дерево по какой либо причине нельзя построить, то будет выводиться сообщение указанное
        в данном параметре; \n

        show_only: принимает объект вида связи, если передан данный параметр, то будут отображаться только связи
        данного вида для переданных знаний (используется если у одного знания из queryset есть несколько связей разных
        видов и необходимо отобразить связи только определённого вида); \n

        hidden_author: принимает объект автора, около знаний данного автора он не указывается; \n

        show_complex: если данный параметр имеет значение True, то на дереве будут отображаться сложные знания.
        В настоящее время для отображения на дереве существует 2 вида сложных знаний: "Таблица", "Тест"
    """
    if not queryset:
        raise EmptyResultSet('Для построения дерева необходим queryset знаний')
    tree_builder = KnowledgeTreeBuilder(queryset, show_only, show_complex)
    tree_context = tree_builder.get_nodes_data_for_tree()
    context = dict(
        tree_num=tree_num,
        empty_tree_message=empty_tree_message,
        hidden_author=hidden_author,
        active_knowledge=queryset,
        **tree_context
    )
    return context


@register.simple_tag
def get_data_by_category(tree_data: dict, category) -> list:
    return tree_data.get(category.pk)


@register.simple_tag
def get_relation_name(relations_names: dict, parent: Znanie, child: Znanie) -> str:
    if not parent:
        return ''
    return relations_names.get((parent.pk, child.pk))


@register.simple_tag
def get_knowledge_counts(data, knowledge):
    counts = data.get(knowledge)
    if not counts:
        return ''
    knowledge_count = counts.get('knowledge_count')
    child_count = counts.get('child_count')
    html = f'<span class="badge bg-danger" title="Общее число знаний (Число дочерних знаний)">' \
           f'{knowledge_count} ({child_count})' \
           f'</span>'
    if knowledge_count == child_count:
        html = f'<span class="badge bg-danger" title="Общее число знаний">' \
               f'{knowledge_count}' \
               f'</span>'
    return mark_safe(html)


@register.simple_tag
def get_category_counts(data, category):
    counts = data.get(category)
    if not counts:
        return ''
    knowledge_count = counts.get('knowledge_count')
    base_knowledge_count = counts.get('base_knowledge_count')
    html = f'<span class="badge bg-info" title="Общее число знаний (Число основных знаний)">' \
           f'{knowledge_count} ({base_knowledge_count})' \
           f'</span>'
    if knowledge_count == base_knowledge_count:
        html = f'<span class="badge bg-info" title="Общее число знаний">' \
               f'{knowledge_count}' \
               f'</span>'
    return mark_safe(html)
