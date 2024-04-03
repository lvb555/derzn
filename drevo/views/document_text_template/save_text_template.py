from django.views.decorators.http import require_POST
from django.http import HttpResponse
from drevo.models import Znanie, TemplateObject
import json


@require_POST
def save_text_template_view(request, **kwargs):
    content = request.POST.get('content')
    text_template_pk = request.POST.get('pk')
    if content is None:
        return HttpResponse(json.dumps({
                    'res': 'error',
                    'errors': ['Отсутсвует поле content, текст шаблона']
                }))

    try:
        zn = Znanie.objects.get(id=text_template_pk)
    except Znanie.DoesNotExist as e:
        return HttpResponse(
                json.dumps({
                    'res': 'error',
                    'errors': [str(e)]
                }),
                content_type='application/json'
            )

    zn.template_objects_set.clear()
    objects = request.POST.getlist('objects')
    if objects:
        for i in objects:
            zn.template_objects_set.add(TemplateObject.objects.get(id=int(i)))
    zn.content = content
    zn.save()

    return HttpResponse(json.dumps({'res': 'ok'}), content_type='application/json')
