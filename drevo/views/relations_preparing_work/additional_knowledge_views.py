from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from drevo.forms import AdditionalKnowledgeForm
from drevo.models import KnowledgeStatuses, Znanie, SpecialPermissions
from pip._vendor import requests
from drevo.relations_tree import get_category_for_knowledge


def check_competence(request) -> bool:
    bz = get_object_or_404(Znanie, pk=request.POST.get('bz_pk'))
    category = get_category_for_knowledge(bz)
    user_competencies = SpecialPermissions.objects.filter(expert=request.user).first()
    if not user_competencies:
        return False
    return True if category in user_competencies.categories.all() else False


@login_required
@require_http_methods(['POST'])
def create_additional_knowledge(request):
    """
        Создание дополнительного знания
    """
    req_data = request.POST
    form = AdditionalKnowledgeForm(data=req_data)
    user = request.user
    if form.is_valid():
        new_kn = form.save(commit=False)
        new_kn.user = user
        new_kn.is_published = True
        new_kn = form.save()
        kn_status = 'PUB' if check_competence(request) else 'PUB_PRE'
        KnowledgeStatuses.objects.create(knowledge=new_kn, status=kn_status, user=user)
    return redirect(request.META['HTTP_REFERER'])


@login_required
@transaction.atomic
def additional_knowledge_update_view(request, kn_pk):
    """
        Страница обновления дополнительного знания
    """
    def get_related_types():
        bz_id, tr_id = request.GET.get('bz_id'), request.GET.get('tr_id')
        url = request.build_absolute_uri(reverse('get_related_tz'))
        resp = requests.get(url=url, params={'bz_id': bz_id, 'tr_id': tr_id})
        tz_data = resp.json()
        related_tz = [('', '-------')]
        if tz_data:
            related_tz += [(tz.get('id'), tz.get('name')) for tz in tz_data.get('related_tz')]
        return related_tz

    knowledge = get_object_or_404(Znanie, pk=kn_pk)
    if 'relation_create_url' not in request.session:
        request.session['relation_create_url'] = request.META['HTTP_REFERER']

    if request.method == 'POST':
        form = AdditionalKnowledgeForm(instance=knowledge, data=request.POST)
        if form.is_valid():
            form.save()
            red_url = request.session.get('relation_create_url')
            del request.session['relation_create_url']
            return redirect(red_url)
    else:
        form = AdditionalKnowledgeForm(instance=knowledge)

    form.fields['tz'].widget.choices = get_related_types()
    return render(request, 'drevo/relations_preparing_page/additional_knowledge_update_page.html', {'form': form})
