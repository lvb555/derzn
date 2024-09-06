from drevo.forms import TemplateObjectForm
from drevo.models import TemplateObject
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.forms.models import model_to_dict
import json


def get_object(pk):
    """
        Получить объект с данным id
    """
    try:
        obj = TemplateObject.objects.get(id=int(pk))
    except TemplateObject.DoesNotExist:
        raise TemplateObject.DoesNotExist(json.dumps({
            'res': 'error',
            'error': f'Объекта с id {pk} не существует'}))
    except ValueError:
        raise ValueError(json.dumps({
            'res': 'error',
            'error': f'Не удалось распознать id {pk}'}))

    return obj


@require_http_methods(["DELETE"])
def document_object_deletion_view(request, doc_pk):
    form = TemplateObjectForm()
    try:
        obj = get_object(request.GET['id'])
    except Exception as e:
        return JsonResponse({
                'res': 'error',
                'error': str(e)
            })

    if obj.availability > 2:
        return JsonResponse({'res': 'err', 'error': 'Нельзя удалить общий объект.'})

    templates_that_use = obj.templates_that_use.all()
    if templates_that_use.count():

        error_text = f'Этот объект используется в следующих шаблонах:<br>'
        error_text += ', '.join([template.name for template in templates_that_use])

        return JsonResponse({'res': 'err', 'error': error_text})

    if not obj.is_leaf_node():
        return JsonResponse({'res': 'err', 'error': 'Нельзя удалить родителя.'})

    if obj.availability == 2:
        return JsonResponse({'res': 'err', 'error': 'Нельзя удалить общий объект.'})

    object_in_json = model_to_dict(obj, exclude=['templates_that_use'])
    obj.delete()

    return JsonResponse({'res': 'ok', 'object': object_in_json, 'select_tree': str(form['connected_to'])})
