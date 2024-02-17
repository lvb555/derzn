import json
from django.http import HttpResponse, HttpResponseRedirect
from django.forms.models import model_to_dict
from django.core import serializers
from django.urls import reverse
from drevo.forms import TurpleForm
from drevo.models import Turple, TurpleElement, TemplateObject


def get_turple(pk):
    """
        Получить словарь с данным id
    """
    try:
        turple = Turple.objects.get(id=int(pk))
    except Turple.DoesNotExist:
        raise Turple.DoesNotExist(json.dumps({
            'res': 'error',
            'error': f'Словаря с id {pk} не существует'}))
    except ValueError:
        raise ValueError(json.dumps({
            'res': 'error',
            'error': f'Не удалось распознать id {pk}'}))

    return turple


def turple_processing_view(request, doc_pk):
    """
        Обработка запросов, касающихся справочников в сервисе создания шаблонов документов
        GET: запрос информации об словаре
        POST: запрос на изменение/создание словаря
    """
    if request.method == 'POST':
        # определить тип действия
        if 'id' in request.POST:
            action = 'edit'
            try:
                turple = get_turple(request.POST["id"])
            except Exception as e:
                return HttpResponse(str(e), content_type='application/json')
        else:
            action = 'create'

        form = TurpleForm(request.POST)

        if form.is_valid():
            new_turple = form.save(commit=(action == 'create'))
            if action == 'edit':
                turple.name = new_turple.name
                turple.availability = int(new_turple.availability)
                turple.weight = new_turple.weight
                turple.save()
            # список элементов справочника
            elements = zip(
                request.POST.getlist('element-id'),
                request.POST.getlist('element-weight'),
                request.POST.getlist('element-var'),
                request.POST.getlist('element-name'))
            related_turple = (turple if action == 'edit' else new_turple)
            for pk, weight, var, value in elements:
                if pk == '':  # создание нового значения справочника
                    TurpleElement.objects.create(
                        value=value,
                        var=(None if var == '' else TemplateObject.objects.get(id=var)),
                        weight=weight,
                        turple=related_turple
                    )
                else:  # изменение существующего значения справочника
                    elem = TurpleElement.objects.get(id=int(pk))
                    elem.value = value
                    elem.weight = weight
                    elem.var = None if var == '' else TemplateObject.objects.get(id=var)
                    elem.turple = related_turple
                    elem.save()

            return HttpResponse(
                json.dumps({
                    'res': 'ok',
                    'turples': json.loads(serializers.serialize("json", Turple.objects.filter(knowledge=new_turple.knowledge)))}),
                content_type='application/json')

        return HttpResponse(
            json.dumps({
                'res': 'validation error',
                'errors': form.errors}),
            content_type='application/json')
    elif request.method == 'GET' and 'id' in request.GET:
        try:
            turple = get_turple(request.GET["id"])
            turple_elements = TurpleElement.objects.filter(turple=turple)
        except Exception as e:
            return HttpResponse(str(e), content_type='application/json')

        return HttpResponse(  # вернуть информацию по требуемому справочнику
            json.dumps({
                'res': 'ok',
                'turple': model_to_dict(turple),
                'elements': json.loads(serializers.serialize('json', turple_elements.all()))}),
            content_type='application/json')
    else:
        return HttpResponseRedirect(reverse('drevo'))
