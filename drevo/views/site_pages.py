from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_http_methods
from drevo.forms.knowledge_create_form import ZnanieCreateForm
from drevo.forms.site_page_create_form import SitePageCreateForm, SitePageRedactForm
from drevo.models import FriendsInviteTerm, Message
from drevo.models.feed_messages import FeedMessage
from users.models import User, MenuSections
from django.db.models import ProtectedError
from users.views import access_sections
from django.contrib import messages
from drevo.models.site_page import SitePage, PageHistory, StatusType

from drevo.utils.common import validate_parameter_int


def site_pages_view(request):
    context = dict(nodes=SitePage.tree_objects.all())
    if request.method == 'POST':
        form = SitePageCreateForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect('site_pages')

    else:
        context['form'] = SitePageCreateForm
    if request.user.is_authenticated:
        context['sections'] = access_sections(request.user)
        context['activity'] = [i for i in context['sections'] if i.startswith('Мои') or
                               i.startswith('Моя')]
        context['link'] = 'users:myprofile'
        invite_count = FriendsInviteTerm.objects.filter(recipient=request.user.id).count()
        context['invite_count'] = invite_count if invite_count else 0
        context['new_knowledge_feed'] = FeedMessage.objects.filter(recipient=request.user, was_read=False).count()
        context['new_messages'] = Message.objects.filter(recipient=request.user, was_read=False).count()
        context['new'] = int(context['new_knowledge_feed']) + int(
            context['invite_count'] + int(context['new_messages']))
        context['pub_user'] = request.user
    context['znanie_form'] = ZnanieCreateForm
    return render(request, "drevo/site_pages.html", context)


def site_page_view(request, pk=None):
    instance = get_object_or_404(SitePage, pk=pk)

    if request.method == 'POST':
        if 'delete' in request.POST:
            # Проверка на наличие связанных объектов
            related_pages = SitePage.objects.filter(parent=instance)
            if related_pages.exists():
                messages.error(request, "Объект содержит подчиненные объекты, поэтому удален быть не может.")
                return redirect('site_page', pk=pk)

            try:
                page_title = instance.page
                instance.delete()
                messages.success(request, f'Страница {page_title} успешно удалена.')
                return redirect('site_pages')
            except ProtectedError:
                messages.error(request, "Невозможно удалить страницу из-за связанных объектов.")
                return redirect('site_page', pk=pk)
        else:
            # Обработка формы редактирования
            form = SitePageRedactForm(request.POST, instance=instance)
            if form.is_valid():
                changed_fields = form.changed_data
                for field in changed_fields:
                    previous_value = form.initial.get(field)
                    new_value = form.cleaned_data.get(field)

                    if field == 'subscribers':
                        previous_value = ', '.join([person.username for person in previous_value])
                        new_value = ', '.join([person.username for person in new_value])

                    PageHistory.objects.create(
                        page=instance,
                        prop=field,
                        previous_value=previous_value,
                        last_value=new_value,
                        staff_member=request.user
                    )

                form.save()
                messages.success(request, "Изменения успешно сохранены.")
                return redirect('site_page', pk=pk)
    else:
        form = SitePageRedactForm(instance=instance)

    context = {
        'current_page': instance,
        'form': form,
        'history': PageHistory.objects.filter(page=instance),
        'has_related_pages': SitePage.objects.filter(base_page=instance).exists(),
        'znanie_form': ZnanieCreateForm
    }

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
            'functional': request.GET.get('functional'),
            'layout': request.GET.get('layout'),
            'design_needed': request.GET.get('design_needed'),
            'design': request.GET.get('design'),
            'help_page_content': request.GET.get('help_page_content'),
            'help_page': request.GET.get('help_page'),
            'notification': request.GET.get('notification'),
            'status_id': request.GET.get('status')
        }

        status_id = validate_parameter_int(filters.get('status_id'), default=None)

        filters = {key: True if value == 'yes' else False if value == 'no' else value for key, value in filters.items()
                   if value and value != 'Выбрать'}

        pages = SitePage.objects.filter(**filters)

        if not pages:
            message = 'Страниц сайта не найдено'

        context = {'all_status': all_status, 'pages': pages, 'message': message,'status_id':status_id}
        return render(request, 'drevo/search_page.html', context)

    else:
        all_status = StatusType.objects.all()
        context = {'all_status': all_status}
        return render(request, 'drevo/search_page.html', context)
