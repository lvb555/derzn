from django import template
from django.db.models import QuerySet
from django.template import RequestContext
from drevo.models import Znanie, Tr, Author

from .knowledge_tree import build_knowledge_tree

register = template.Library()


@register.filter()
@register.inclusion_tag('drevo/tags/algorithm_tree.html', takes_context=True)
def build_algorithm_tree(context: RequestContext,
                         queryset: QuerySet[Znanie],
                         ):
    return build_knowledge_tree(context, queryset)