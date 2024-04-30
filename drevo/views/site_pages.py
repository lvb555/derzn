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
    if request.method == 'GET' and 'searchForm' in request.GET:
        all_status = StatusType.objects.all()
        message = 'Результаты поиска:'

        filters = {
            'functional': request.GET.get('functional', False) == 'on',
            'layout': request.GET.get('layout', False) == 'on',
            'design_needed': request.GET.get('design_needed', False) == 'on',
            'design': request.GET.get('design', False) == 'on',
            'help_page_content': request.GET.get('help_page_content', False) == 'on',
            'help_page': request.GET.get('help_page', False) == 'on',
            'notification': request.GET.get('notification', False) == 'on',
            'status_id': request.GET.get('status')
        }

        query = Q()
        for key, value in filters.items():
            if value:
                query.add(Q(**{key: value}), Q.AND)

        pages = SitePage.objects.filter(query)
        if not pages:
            message = 'Страниц сайта не найдено'

        context = {'all_status': all_status, 'pages': pages, 'message': message}
        return render(request, 'drevo/search_page.html', context)

    else:
        all_status = StatusType.objects.all()
        context = {'all_status': all_status}
        return render(request, 'drevo/search_page.html', context)
