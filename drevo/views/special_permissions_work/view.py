from django.db.models import F, Count, QuerySet
from django.views.decorators.http import require_http_methods
from django.views.generic import TemplateView
from django.shortcuts import redirect
from .mixins import CandidatesMixin
from drevo.models import Category, SpecialPermissions, Znanie
from users.models import User


class SpecialPermissionsView(TemplateView, CandidatesMixin):
    """
        Добавление особых прав пользователям.
        Формируем страницу с тремя блоками:
        1. Назначение прав экспертов (строится дерево категорий для которых есть кандидаты в эксперты)
        2. Назначение прав редакторов (отображается список пользователей, которым можно назначить/снять права редактора)
        3. Назначение прав руководителей (строится дерево категорий для которых есть кандидаты в руководители)
    """
    template_name = 'drevo/special_permissions_page/add_users_special_permissions.html'

    @staticmethod
    def get_candidates_tree_data(candidates_data: dict) -> dict:
        """
            Метод для получения данных для построения дерева категорий для которых есть кандидаты
            Данные словаря на выходе:
            1. candidates_count - Кол-во кандидатов для каждой категории {<int:category_pk>: <int:candidates_count>}
            2. nodes - Категории
        """
        tree_data = {'candidates_count': None, 'nodes': None}
        tree_categories = list()
        for _, data in candidates_data.items():
            categories = data.get('categories')
            tree_categories.extend(category_pk for category_pk in categories.keys())
        categories = Category.objects.filter(pk__in=set(tree_categories))
        tree_data['candidates_count'] = {category.pk: tree_categories.count(category.id) for category in categories}
        active_nodes = list()
        for cat in categories:
            active_nodes.extend(list(cat.get_ancestors()))
        nodes_pk = list(cat.pk for cat in set(active_nodes)) + list(tree_data['candidates_count'].keys())
        tree_data['nodes'] = Category.tree_objects.exclude(is_published=False).filter(pk__in=nodes_pk)
        return tree_data

    def get_context_data(self, **kwargs):
        context = super(SpecialPermissionsView, self).get_context_data(**kwargs)

        candidates = self.get_all_candidates()
        experts, admins = candidates.get('experts'), candidates.get('admins')
        context.update({'experts': experts, 'admins': admins})

        # Дерево для кандидатов в эксперты
        experts_tree_data = self.get_candidates_tree_data(candidates_data=experts)
        context.update({f'experts_{key}': value for key, value in experts_tree_data.items()})
        context['experts_checked_category'] = ''

        # Дерево для кандидатов в руководители
        admins_tree_data = self.get_candidates_tree_data(candidates_data=admins)
        context.update({f'admins_{key}': value for key, value in admins_tree_data.items()})
        context['admins_checked_category'] = ''

        # Блок кандидатов в руководители
        search_result = None
        if editor_last_name := self.request.GET.get('editor_last_name'):
            search_result = User.objects.filter(last_name__icontains=editor_last_name)
            context['editor_last_name'] = editor_last_name
        context['editors'] = User.objects.all() if not search_result else search_result
        context['last_set_editors'] = ''
        return context


@require_http_methods(["POST"])
def set_users_as_editor(request):
    """
        Назначить права редактора пользователям
    """
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
    """
        Страница со списком кандидатов в эксперты
    """
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
    """
        Назначить пользователям права эксперта
    """
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


class AdminsCandidatesListView(TemplateView, CandidatesMixin):
    """
        Страница со списком кандидатов в руководители
    """
    template_name = 'drevo/special_permissions_page/admins_candidates_page.html'

    def get_context_data(self, **kwargs):
        context = super(AdminsCandidatesListView, self).get_context_data(**kwargs)
        category = Category.objects.get(pk=self.kwargs.get('category_pk'))
        context['category'] = category
        candidates = self.get_admin_candidates()
        candidates_by_category = list()
        for user_pk, user_data in candidates.items():
            if category.pk in user_data['categories'].keys():
                user = User.objects.get(pk=user_pk)
                knowledge_count, expertise_count = user_data['categories'][category.pk]
                candidates_by_category.append((user_pk, user.get_full_name(), knowledge_count, expertise_count))
        context['candidates'] = candidates_by_category
        return context


@require_http_methods(['POST'])
def set_users_as_admin(request, category_pk):
    """
        Назначить пользователям права руководителя
    """
    users_pk = [int(elm.replace('candidate_', '')) for elm in request.POST.keys() if elm != 'csrfmiddlewaretoken']
    if not users_pk:
        return redirect('special_permissions_page')
    users = User.objects.filter(pk__in=users_pk)
    updated_users = list()
    for user in users:
        user.is_director = True
        updated_users.append(user)
    User.objects.bulk_update(updated_users, ['is_director'])

    category = Category.objects.get(pk=category_pk)
    for user in users:
        user_permissions, _ = SpecialPermissions.objects.get_or_create(expert=user)
        user_permissions.admin_competencies.add(category)
        user_permissions.save()
    return redirect('special_permissions_page')


class UsersSpecialPermissionsView(TemplateView, CandidatesMixin):
    """
        Страница с описанием особых прав пользователя
    """
    template_name = 'drevo/special_permissions_page/user_special_permissions.html'

    @staticmethod
    def get_user_permissions_tree_data(competencies_data: dict) -> QuerySet:
        """
            Метод для получения данных для построения дерева категорий, которые входят в компетенцию пользователя
        """
        tree_categories = list()
        tree_categories.extend(category_pk for category_pk in competencies_data.keys())
        categories = Category.objects.filter(pk__in=set(tree_categories))
        active_nodes = list()
        for cat in categories:
            active_nodes.extend(list(cat.get_ancestors()))
        nodes_pk = list(cat.pk for cat in set(active_nodes)) + list(competencies_data.keys())
        nodes = Category.tree_objects.exclude(is_published=False).filter(pk__in=nodes_pk)
        return nodes

    @staticmethod
    def get_competencies_data_by_categories(categories_pk: list, all_competencies_data: dict) -> dict:
        """
            Метод для получения данных о кол-ве созданных знаний и экспертиз
            пользователя в рамках той или иной компетенции (категории)
            Результирующие данные:
            {<int:category_pk>: {knowledge_count: <int:count>, expertise_count: <int:count>}...}
        """
        return {
            category: {'knowledge_count': knowledge_count, 'expertise_count': expertise_count}
            for category, (knowledge_count, expertise_count) in all_competencies_data.items()
            if category in categories_pk
        }

    def get_context_data(self, **kwargs):
        context = super(UsersSpecialPermissionsView, self).get_context_data(**kwargs)
        user_pk = self.request.user.pk
        permissions = (
            SpecialPermissions.objects
            .prefetch_related('categories', 'admin_competencies')
            .filter(expert_id=user_pk)
        ).first()

        if not permissions:
            return context

        competencies_data = self.get_user_competencies_data(user_pk)
        # Получение данных по компетенциям пользователя как эксперта
        expert_competencies = permissions.categories.values_list('pk', flat=True)
        context['expert_comp'] = self.get_competencies_data_by_categories(expert_competencies, competencies_data)
        context['experts_nodes'] = self.get_user_permissions_tree_data(competencies_data=context['expert_comp'])
        # Получение данных по работе пользователя как редактора



        # Получение данных по компетенциям пользователя как руководителя
        admin_competencies = permissions.admin_competencies.values_list('pk', flat=True)
        context['admin_comp'] = self.get_competencies_data_by_categories(admin_competencies, competencies_data)
        context['admins_nodes'] = self.get_user_permissions_tree_data(competencies_data=context['admin_comp'])
        context['permissions'] = permissions
        return context
