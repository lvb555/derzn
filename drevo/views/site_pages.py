from django.shortcuts import render, get_object_or_404, redirect

from drevo.forms.site_page_create_form import SitePageCreateForm, SitePageRedactForm
from drevo.models.site_page import SitePage, PageHistory


def site_pages_view(request):
    context = dict(nodes=SitePage.tree_objects.all())
    if request.method == 'POST':
        form = SitePageCreateForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect('site_pages')

    else:
        context['form'] = SitePageCreateForm
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
