from django.db.models import QuerySet
from django.template import Library

from drevo.utils.knowledge_tree_builder import KnowledgeTreeBuilder
from drevo.models import Znanie, Category

register = Library()


@register.inclusion_tag('drevo/tags/knowledge_tree.html')
def build_knowledge_tree(queryset: QuerySet[Znanie], tree_num: int = 1):
    """
        Тег для построения дерева знаний
        tree_num: номер дерева (на случай если необходимо на одной странице создать несколько деревьев)
    """
    tree_builder = KnowledgeTreeBuilder(queryset)
    tree_context = tree_builder.get_nodes_data_for_tree()
    context = dict(tree_num=tree_num, active_knowledge=queryset, **tree_context)
    return context


@register.simple_tag
def get_data_by_category(tree_data: dict, category) -> list:
    return tree_data.get(category.pk)
