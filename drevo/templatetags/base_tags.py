from django.db.models import QuerySet
from django.template import Library
from drevo.models import Tr, Tz
register = Library()


@register.simple_tag
def get_relation_types() -> QuerySet[Tr]:
    r_types = Tr.objects.filter(is_systemic=False).order_by('name')
    return r_types


@register.simple_tag
def get_knowledge_types() -> QuerySet[Tz]:
    kn_types = Tz.objects.filter(is_systemic=False).order_by('name')
    return kn_types
