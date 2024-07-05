from django.views.decorators.http import require_POST
from django.http import JsonResponse
from drevo.models import Znanie, TemplateObject
import json


@require_POST
def save_text_template_view(request, **kwargs):
    """
        Сохранение шаблона текста документа
    """
    content = request.POST.get('content')
    text_template_pk = request.POST.get('pk')
    if content is None:
        return JsonResponse({
                    'res': 'error',
                    'errors': ['Отсутсвует поле content, текст шаблона']
                })

    try:
        zn = Znanie.objects.get(id=text_template_pk)
    except Znanie.DoesNotExist as e:
        return JsonResponse({
                    'res': 'error',
                    'errors': [str(e)]
                }
            )
    zn.template_objects_set.set(request.POST.getlist('objects'))
    zn.content = content
    zn.save()

    return JsonResponse({'res': 'ok'})
