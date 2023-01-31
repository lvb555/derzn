from django.shortcuts import render, get_object_or_404
from .models import Help


def help_view(request, pk=None):
    context = dict()
    if pk:
        cur_help = get_object_or_404(Help, pk=pk)
        context['active_nodes'] = cur_help.get_ancestors()
        context['cur_help'] = cur_help
    context['nodes'] = Help.tree_objects.exclude(is_published=False)
    return render(request, "help/help.html", context)
