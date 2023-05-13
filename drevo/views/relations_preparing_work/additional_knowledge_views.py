from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404, render
from django.views.decorators.http import require_http_methods

from drevo.forms import AdditionalKnowledgeForm, ZnImageFormSet
from drevo.models import KnowledgeStatuses, Znanie, SpecialPermissions
from drevo.utils.preparing_relations import PreparingRelationsMixin


@login_required
@require_http_methods(['POST'])
def create_additional_knowledge(request):
    """
        Создание дополнительного знания
    """
    req_data = request.POST
    form = AdditionalKnowledgeForm(data=req_data)
    image_form = ZnImageFormSet(req_data, request.FILES)
    user = request.user
    if form.is_valid() and image_form.is_valid():
        new_kn = form.save(commit=False)
        new_kn.user = user
        new_kn.is_published = True
        new_kn.save()

        image_form.instance = new_kn
        image_form.save()

        relation_utils = PreparingRelationsMixin()
        bz = get_object_or_404(Znanie, pk=request.POST.get('bz_pk'))
        kn_status = 'PUB' if relation_utils.check_competence(request.user, bz) else 'PUB_PRE'
        KnowledgeStatuses.objects.create(knowledge=new_kn, status=kn_status, user=user)
        return JsonResponse(data={'name': new_kn.name, 'value': new_kn.pk, 'bz_pk': req_data.get('bz_pk')}, status=200)
    return JsonResponse(data={}, status=400)


@login_required
@transaction.atomic
def additional_knowledge_update_view(request, kn_pk):
    """
        Страница обновления дополнительного знания
    """
    knowledge = get_object_or_404(Znanie, pk=kn_pk)
    if 'relation_create_url' not in request.session:
        request.session['relation_create_url'] = request.META['HTTP_REFERER']

    if request.method == 'POST':
        form = AdditionalKnowledgeForm(instance=knowledge, data=request.POST)
        image_form = ZnImageFormSet(request.POST, request.FILES, instance=knowledge)
        if form.is_valid() and image_form.is_valid():
            form.save()
            image_form.save()
            red_url = request.session.get('relation_create_url')
            del request.session['relation_create_url']
            return redirect(red_url)
    else:
        form = AdditionalKnowledgeForm(instance=knowledge)
        image_form = ZnImageFormSet(instance=knowledge)
    bz_id, tr_id = request.GET.get('bz_id'), request.GET.get('tr_id')
    context = {'form': form, 'image_form': image_form, 'bz_id': bz_id, 'tr_id': tr_id, 'tz_id': knowledge.tz_id}
    return render(request, 'drevo/relations_preparing_page/additional_knowledge_update_page.html', context)
