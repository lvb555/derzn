from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.views.generic import TemplateView
from mptt.querysets import TreeQuerySet

from .mixins import UserPermissionsMixin
from drevo.models import Category, SpecialPermissions
from users.models import User


class SpecialPermissionsDeleteView(TemplateView, UserPermissionsMixin):
    """
        Удаление особых прав пользователей.
        Страница состоит из трёх блоков:
        1. Удаление прав эксперта (строится дерево категорий экспертов)
        2. Удаление прав редактора (отображается список редакторов)
        3. Удаление прав руководителя (строится дерево категорий руководителей)
    """
    template_name = 'drevo/special_permissions_page/delete_users_special_permissions.html'

    @staticmethod
    def get_users_tree_data(categories: list[int]) -> TreeQuerySet:
        """
            Метод для получения данных для построения дерева категорий для пользователей с особыми правами
            Данные словаря на выходе:
            1. candidates_count - Кол-во кандидатов для каждой категории {<int:category_pk>: <int:candidates_count>}
            2. nodes - Категории
        """
        categories = Category.tree_objects.exclude(is_published=False).filter(pk__in=categories)
        nodes = Category.tree_objects.get_queryset_ancestors(categories, include_self=True)
        return nodes

    def get_context_data(self, **kwargs):
        context = super(SpecialPermissionsDeleteView, self).get_context_data(**kwargs)
        # Блок удаления прав экспертов
        experts_data = self.get_experts_for_delete()
        context['experts_candidates_count'] = experts_data
        context['experts_nodes'] = self.get_users_tree_data(experts_data.keys())

        # Блок удаления прав редакторов
        if editor_last_name := self.request.GET.get('editor_last_name'):
            context['editor_last_name'] = editor_last_name
        context['editors'] = self.get_editors_data(last_name=self.request.GET.get('editor_last_name'))

        # Блок удаления прав руководителей
        admins_data = self.get_admins_for_delete()
        context['admins_candidates_count'] = admins_data
        context['admins_nodes'] = self.get_users_tree_data(admins_data.keys())
        return context


class ExpertsPermissionsDeleteView(TemplateView, UserPermissionsMixin):
    """
        Страница "Удаление прав эксперта"
    """
    template_name = 'drevo/special_permissions_page/deleting_experts_permissions.html'

    def get_context_data(self, **kwargs):
        context = super(ExpertsPermissionsDeleteView, self).get_context_data(**kwargs)
        category = get_object_or_404(Category, pk=self.kwargs.get('category_pk'))
        experts_data_raw = self.get_experts_for_delete(for_category=category)
        experts = User.objects.filter(pk__in=experts_data_raw.keys())
        experts_data = [(expert.pk, expert.get_full_name(), len(experts_data_raw.get(expert.pk))) for expert in experts]
        context['category'] = category
        context['experts_data'] = experts_data
        return context


@require_http_methods(['POST'])
def delete_competence_expert(request, category_pk):
    """
        Удалить компетенцию для эксперта/экспертов
    """
    experts = [int(req_data.split('_')[1]) for req_data in request.POST if req_data != 'csrfmiddlewaretoken']
    permissions = SpecialPermissions.objects.filter(expert_id__in=experts)
    for expert_perms in permissions:
        expert_perms.categories.remove(category_pk)
    return redirect('delete_special_permissions_page')


class ExpertKnowledgeView(TemplateView, UserPermissionsMixin):
    """
        Страница со списком знаний и экспертиз, которые были созданы экспертом в рамках определённой компетенции
    """
    template_name = 'drevo/special_permissions_page/expert_competence_knowledge_page.html'

    def get_context_data(self, **kwargs):
        context = super(ExpertKnowledgeView, self).get_context_data(**kwargs)
        category_pk = self.kwargs.get('category_pk')
        expert_pk = self.kwargs.get('expert_pk')
        category = get_object_or_404(Category, pk=category_pk)
        data = self.get_experts_for_delete(for_category=category)
        knowledge_data = {'knowledge': list(), 'expertise': list()}
        for knowledge in data.get(expert_pk):
            if 'is_expertise' not in knowledge.__dict__.keys() or knowledge.is_expertise:
                knowledge_data['expertise'].append(knowledge)
            else:
                knowledge_data['knowledge'].append(knowledge)
        context['knowledge_data'] = knowledge_data
        context['expert'] = get_object_or_404(User, pk=expert_pk)
        context['category'] = category
        context['backup_url'] = reverse('deleting_experts_permissions_page', kwargs={'category_pk': category_pk})
        return context


@require_http_methods(['POST'])
def delete_editor_permissions(request):
    """
        Удалить права редактора
    """
    editors_for_delete = [int(req_data.split('_')[1]) for req_data in request.POST if req_data != 'csrfmiddlewaretoken']
    if not editors_for_delete:
        return redirect('delete_special_permissions_page')
    editors = User.objects.prefetch_related('expert').filter(pk__in=editors_for_delete)
    updated_user_data = list()
    updated_perm_data = list()
    for editor in editors:
        editor.is_redactor = False
        updated_user_data.append(editor)
        editor_perm = editor.expert
        editor_perm.editor = False
        updated_perm_data.append(editor_perm)
    User.objects.bulk_update(updated_user_data, ['is_redactor'])
    SpecialPermissions.objects.bulk_update(updated_perm_data, ['editor'])
    return redirect('delete_special_permissions_page')


class AdminsPermissionsDeleteView(TemplateView, UserPermissionsMixin):
    """
        Страница "Удаление прав руководителя"
    """
    template_name = 'drevo/special_permissions_page/deleting_admins_permissions.html'

    def get_context_data(self, **kwargs):
        context = super(AdminsPermissionsDeleteView, self).get_context_data(**kwargs)
        category = get_object_or_404(Category, pk=self.kwargs.get('category_pk'))
        admins_data_raw = self.get_admins_for_delete(for_category=category)
        admins = User.objects.filter(pk__in=admins_data_raw.keys())
        admins_data = [(admin.pk, admin.get_full_name(), admins_data_raw.get(admin.pk)) for admin in admins]
        context['category'] = category
        context['admins_data'] = admins_data
        return context


@require_http_methods(['POST'])
def delete_competence_admin(request, category_pk):
    """
        Удалить компетенцию для руководителя/руководителей
    """
    admins = [int(req_data.split('_')[1]) for req_data in request.POST if req_data != 'csrfmiddlewaretoken']
    permissions = SpecialPermissions.objects.filter(expert_id__in=admins)
    for admin_perms in permissions:
        admin_perms.admin_competencies.remove(category_pk)
    return redirect('delete_special_permissions_page')
