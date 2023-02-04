from django.shortcuts import render, get_object_or_404
from .models import Help


def help_view(request, pk=None):
    """
    Представление для страницы помощь
    :param request:
    :param pk:
    :return:
    """
    context = dict(nodes=Help.tree_objects.exclude(is_published=False))
    # Если на страницу "Помощь" перешли с другой страницы,
    # то на основе тегов взятых из url ищем раздел помощи по данной странице.
    if (referer := request.META.get('HTTP_REFERER')) and (not pk):
        ref_url = referer.split('/')[3:] if '?' not in referer else referer[:referer.index('?')].split('/')[3:]
        ref_data = [elm for elm in ref_url if elm and elm.isalpha()]
        queryset = Help.objects.prefetch_related('url_tag').filter(url_tag__name__in=ref_data).distinct()
        ref_data.sort()
        for help_obj in queryset:
            if list(help_obj.url_tag.all().values_list('name', flat=True)) == ref_data:
                context['cur_help'] = help_obj
                context['active_nodes'] = help_obj.get_ancestors()
                break
    # Если был передан идентификатор раздела помощи то отображаем данные о нём.
    # На дереве открытыми ветвями будут только те, которые идут до текущего раздела.
    if pk:
        cur_help = get_object_or_404(Help, pk=pk)
        context['active_nodes'] = cur_help.get_ancestors()
        context['cur_help'] = cur_help
    return render(request, "help/help.html", context)
