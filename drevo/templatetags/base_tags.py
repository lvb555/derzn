import os
from django.db.models import QuerySet
from django.template import Library
from drevo.models import Tr, Tz
register = Library()


@register.simple_tag
def get_relation_types() -> QuerySet[Tr]:
    r_types = Tr.objects.filter(is_systemic=False).order_by('name')
    return r_types


@register.simple_tag
def get_knowledge_types(specific_type=None) -> QuerySet[Tz]:
    if specific_type:
        kn_types = Tz.objects.get(name=specific_type)
    else:
        kn_types = Tz.objects.filter(is_systemic=False).order_by('name')
    return kn_types


@register.simple_tag
def url_replace(request, field, value):
    dict_ = request.GET.copy()
    dict_[field] = value
    return dict_.urlencode()


@register.filter
def repeat_for_times(value, count):
    return value * count


@register.filter
def get_extension_or_filename(file_name, part):
    return os.path.splitext(os.path.basename(file_name))[int(part)][int(part):]
