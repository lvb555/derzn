from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_http_methods
from drevo.forms.knowledge_create_form import ZnanieCreateForm
from drevo.forms.site_page_create_form import SitePageCreateForm, SitePageRedactForm
from drevo.models.site_page import SitePage, PageHistory, StatusType


def site_pages_view(request):
    context = dict(nodes=SitePage.tree_objects.all())
    if request.method == 'POST':
        form = SitePageCreateForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect('site_pages')

    else:
        context['form'] = SitePageCreateForm
    context['znanie_form'] = ZnanieCreateForm
    return render(request, "drevo/site_pages.html", context)


def site_page_view(request, pk=None):
    instance = get_object_or_404(SitePage, pk=pk)
    if request.method == 'POST':
        form = SitePageRedactForm(request.POST, instance=instance)

        if form.is_valid():
            changed_fields = form.changed_data
            if changed_fields:
                for field in changed_fields:
                    if field == 'subscribers':
                        PageHistory.objects.create(
                            page=instance,
                            prop=field,
                            previous_value=', '.join([person.username for person in form.initial.get('subscribers')]),
                            last_value=', '.join([person.username for person in form.cleaned_data.get('subscribers')]),
                            staff_member=request.user
                        )
                    else:
                        PageHistory.objects.create(
                            page=instance,
                            prop=field,
                            previous_value=form.initial.get(field),
                            last_value=form.cleaned_data.get(field),
                            staff_member=request.user
                        )
                form.save()
        return redirect('site_page', pk)

    context = {}
    context['current_page'] = get_object_or_404(SitePage, pk=pk)
    context['form'] = SitePageRedactForm(instance=context['current_page'])
    context['history'] = PageHistory.objects.filter(page=instance)

    return render(request, "drevo/site_page.html", context)

@require_http_methods(['POST'])
def create_new_zn(request):
    form = ZnanieCreateForm(data=request.POST)

    if form.is_valid():
        knowledge = form.save(commit=False)
        knowledge.is_published = True
        knowledge.user = request.user
        knowledge.save()

        return JsonResponse(data={'zn_name': knowledge.name, 'zn_id': knowledge.id}, status=200)

    return JsonResponse(data={}, status=400)


def search_page(request):
    all_status = StatusType.objects.all()
    filters = {
        'functional': request.GET.get('functional', False),
        'layout': request.GET.get('layout', False),
        'design_needed': request.GET.get('design_needed', False),
        'design': request.GET.get('design', False),
        'help_page_content': request.GET.get('help_page_content', False),
        'help_page': request.GET.get('help_page', False),
        'notification': request.GET.get('notification', False),
        'status_id': request.GET.get('status')
    }

    query = Q()
    for key, value in filters.items():
        if key == 'status_id' and value:
            query.add(Q(status_id=value), Q.AND)
        elif value:
            query.add(Q(**{key: True}), Q.AND)

    pages = SitePage.objects.filter(query)
    context = {'all_status': all_status, 'pages': pages}
    return render(request, 'drevo/search_page.html', context)
