from django.views.decorators.http import require_http_methods
from django.views.generic import TemplateView
from django.shortcuts import reverse, redirect
from .mixins import CandidatesMixin
from drevo.models import Category, SpecialPermissions
from users.models import User


class SpecialPermissionsView(TemplateView, CandidatesMixin):
    template_name = 'drevo/special_permissions_page/add_users_special_permissions.html'

    def get_context_data(self, **kwargs):
        context = super(SpecialPermissionsView, self).get_context_data(**kwargs)
        context['experts'] = self.get_expert_candidates()
        context['admins'] = self.get_admin_candidates()

        # Дерево для экспертов
        categories_list = list()
        for _, data in context['experts'].items():
            categories = data.get('categories')
            categories_list.extend(category_pk for category_pk in categories.keys())
        categories = Category.objects.filter(pk__in=set(categories_list))
        context['categories_with_candidates'] = {category.pk: categories_list.count(category.id) for category in
                                                 categories}
       # print(context['categories_with_candidates'])
        context['candidates_cnt'] = sum(list(context['categories_with_candidates'].values()))
        #print(categories)
        active_nodes = list()
        for cat in categories:
            active_nodes.extend(list(cat.get_ancestors()))
        active_nodes = set(active_nodes)
        #print(active_nodes)
        context['nodes'] = Category.tree_objects.exclude(is_published=False)

        context['active_nodes'] = active_nodes

        # Дерево для админов
        categories_list = list()
        for _, data in context['admins'].items():
            categories = data.get('categories')
            categories_list.extend(category_pk for category_pk in categories.keys())
        categories = Category.objects.filter(pk__in=set(categories_list))
        context['admins_categories_with_candidates'] = {category.pk: categories_list.count(category.id) for category in
                                                 categories}
        # print(context['categories_with_candidates'])
        context['admins_candidates_cnt'] = sum(list(context['admins_categories_with_candidates'].values()))
        # print(categories)
        active_nodes = list()
        for cat in categories:
            active_nodes.extend(list(cat.get_ancestors()))
        active_nodes = set(active_nodes)
        # print(active_nodes)
        context['admins_nodes'] = Category.tree_objects.exclude(is_published=False)

        context['admins_active_nodes'] = active_nodes

        search_result = None
        if editor_last_name := self.request.GET.get('editor_last_name'):
            search_result = User.objects.filter(last_name__icontains=editor_last_name)
            context['editor_last_name'] = editor_last_name
        context['editors'] = User.objects.all() if not search_result else search_result
        return context


@require_http_methods(["POST"])
def set_users_as_editor(request):
    users_pk = [int(elm.replace('editor_', '')) for elm in request.POST.keys() if elm != 'csrfmiddlewaretoken']
    if not users_pk:
        return redirect('special_permissions_page')
    users = User.objects.filter(pk__in=users_pk)
    updated_users = list()
    for user in users:
        user.is_redactor = True
        updated_users.append(user)
    User.objects.bulk_update(updated_users, ['is_redactor'])

    updated_permissions = list()
    for user in users:
        user_permissions, _ = SpecialPermissions.objects.get_or_create(expert=user)
        user_permissions.editor = True
        updated_permissions.append(user_permissions)
    SpecialPermissions.objects.bulk_update(updated_permissions, ['editor'])
    return redirect('special_permissions_page')


class ExpertsCandidatesListView(TemplateView, CandidatesMixin):
    template_name = 'drevo/special_permissions_page/experts_candidates_page.html'

    def get_context_data(self, **kwargs):
        context = super(ExpertsCandidatesListView, self).get_context_data(**kwargs)
        category = Category.objects.get(pk=self.kwargs.get('category_pk'))
        context['category'] = category
        candidates = self.get_expert_candidates()
        candidates_by_category = list()
        for user_pk, user_data in candidates.items():
            if category.pk in user_data['categories'].keys():
                user = User.objects.get(pk=user_pk)
                candidates_by_category.append((user_pk, user.get_full_name(), user_data['categories'][category.pk]))
        context['candidates'] = candidates_by_category
        return context


@require_http_methods(['POST'])
def set_users_as_expert(request, category_pk):
    users_pk = [int(elm.replace('candidate_', '')) for elm in request.POST.keys() if elm != 'csrfmiddlewaretoken']
    if not users_pk:
        return redirect('special_permissions_page')
    users = User.objects.filter(pk__in=users_pk)
    updated_users = list()
    for user in users:
        user.is_expert = True
        updated_users.append(user)
    User.objects.bulk_update(updated_users, ['is_expert'])

    category = Category.objects.get(pk=category_pk)
    for user in users:
        user_permissions, _ = SpecialPermissions.objects.get_or_create(expert=user)
        user_permissions.categories.add(category)
        user_permissions.save()
    return redirect('special_permissions_page')

