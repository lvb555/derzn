from django import template

register = template.Library()


@register.inclusion_tag('drevo/tags/pagination_tag.html', takes_context=True)
def pagination_tag(context):
    paginator = context['paginator']
    cur_page_num = context['page_obj'].number
    elided_page_range = paginator.get_elided_page_range(
        cur_page_num)
    context['elided_page_range'] = elided_page_range
    return context
