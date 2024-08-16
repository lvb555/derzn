from django.forms import model_to_dict
from django.views.decorators.http import require_http_methods
from drevo.models import TemplateObject
from django.http import JsonResponse
from django.db.models import Q


@require_http_methods(['GET'])
def object_tree_correctnes_check_view(request, doc_pk):
    groups = TemplateObject.objects.filter(Q(knowledge=doc_pk, availability=0) | Q(user=request.user, availability=1) | Q(user=None, availability=1) | Q(availability=2)).filter(is_main=True)
    groups_leafs = []
    for group in groups:
        if group.is_leaf_node():
            groups_leafs.append(model_to_dict(group, exclude=['templates_that_use']))

    return JsonResponse({'group_leafs': groups_leafs})