from django.views.decorators.http import require_http_methods
from django.http import HttpResponse
from drevo.forms import TemplateObjectForm
from django.db.models import Q
from drevo.models import TemplateObject
from django.forms.models import model_to_dict
from django.core import serializers
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


@require_http_methods(["GET", "POST", "DELETE"])
def document_object_processing_view(request, doc_pk):
    """
    Обработка запросов, касающихся объектов в сервисе создания шаблонов документов
    GET: запрос информации об объекте
    POST: запрос на изменение объекта/создание нового
    """
    # ответ на запрос информации об объекте
    if request.method == 'GET' and 'id' in request.GET:

        try:
            obj = get_object(request.GET['id'])
            obj_in_dict = model_to_dict(obj)
            obj_in_dict['templates_that_use'] = [i.id for i in obj_in_dict['templates_that_use']]
        except Exception as e:
            return HttpResponse(
                json.dumps({
                    'res': 'error',
                    'error': str(e)
                }),
                content_type='application/json')

        return HttpResponse(json.dumps({'res': 'ok', 'object': obj_in_dict}))

    # создание/изменение объекта
    elif request.method == 'POST':
        form = TemplateObjectForm(request.POST)
        obj_to_return = None

        if not form.is_valid():
            return HttpResponse(
                json.dumps
                ({
                    'res': 'validation error',
                    'errors': form.errors
                }),
                content_type='application/json')
        try:
            form.cleaned_data['type_of'] = int(form.cleaned_data['type_of']) if form.cleaned_data['type_of'] != '' else 0
            form.cleaned_data['weight'] = int(form.cleaned_data['weight']) if form.cleaned_data['weight'] is not None else 100
            form.cleaned_data['availability'] = int(form.cleaned_data['availability'])
            form.cleaned_data['fill_title'] = form.cleaned_data['fill_title'] if form.cleaned_data['fill_title'] is not None else ''
            form.cleaned_data['comment'] = form.cleaned_data['comment'] if form.cleaned_data['comment'] is not None else ''
            form.cleaned_data['structure'] = int(form.cleaned_data['structure'])
            if form.cleaned_data['action'] == 'create':
                obj_to_return = TemplateObject.objects.create(
                    name=form.cleaned_data['name'],
                    structure=form.cleaned_data['structure'],
                    is_main=form.cleaned_data['is_main'],
                    availability=form.cleaned_data['availability'],
                    weight=form.cleaned_data['weight'],
                    fill_title=form.cleaned_data['fill_title'],
                    subscription=form.cleaned_data['subscription'],
                    optional=form.cleaned_data['optional'],
                    type_of=form.cleaned_data['type_of'],
                    knowledge=form.cleaned_data['knowledge'],  # переделать под параметр doc_pk
                    connected_to=form.cleaned_data['connected_to'],
                    turple=form.cleaned_data['turple'],
                    comment=form.cleaned_data['comment'],
                    user=request.user)
            elif form.cleaned_data['action'] == 'edit':
                obj_to_return = form.cleaned_data['pk']
                form.cleaned_data['pk'].name = form.cleaned_data['name']
                form.cleaned_data['pk'].structure = form.cleaned_data['structure']
                form.cleaned_data['pk'].is_main = form.cleaned_data['is_main']
                form.cleaned_data['pk'].availability = form.cleaned_data['availability']
                form.cleaned_data['pk'].weight = form.cleaned_data['weight']
                form.cleaned_data['pk'].fill_title = form.cleaned_data['fill_title']
                form.cleaned_data['pk'].subscription = form.cleaned_data['subscription']
                form.cleaned_data['pk'].optional = form.cleaned_data['optional']
                form.cleaned_data['pk'].type_of = form.cleaned_data['type_of']
                form.cleaned_data['pk'].turple = form.cleaned_data['turple']
                form.cleaned_data['pk'].comment = form.cleaned_data['comment']
                form.cleaned_data['pk'].connected_to = form.cleaned_data['connected_to']
                form.cleaned_data['pk'].save()
        except Exception as e:
            return HttpResponse(json.dumps({'res': 'database error', 'error': e}), content_type='application/json')
        return HttpResponse(json.dumps({'res': 'ok', 'object': model_to_dict(obj_to_return)}), content_type='application/json')
    elif request.method == 'DELETE':
        obj = get_object(request.DELETE["id"])
        return HttpResponse(json.dumps({'res': 'ok'}), content_type='application/json')
