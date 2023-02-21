from django.db.models import QuerySet
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.views.generic import TemplateView
from django.shortcuts import redirect, get_object_or_404
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

    def clear_page_session(self) -> None:
        """
            Метод для очистки данных сессии
            (если переход на страницу был совершён с url не связанный со страницами особых прав) о:
            1. Назначенных редакторах за текущую сессию
            2. Категориях в которых были выданы права эксперта за текущую сессию
            3. Категориях в которых были выданы права руководителя за текущую сессию
        """
        ref_url_elms = self.request.META.get('HTTP_REFERER')
        if 'special_permissions' in ref_url_elms:
            return
        session_data = self.request.session
        if 'experts_checked_category' in session_data.keys():
            del self.request.session['experts_checked_category']
        if 'admins_checked_category' in session_data.keys():
            del self.request.session['admins_checked_category']
        if 'last_set_editors' in session_data.keys():
            del self.request.session['last_set_editors']

    def get_context_data(self, **kwargs):
        context = super(SpecialPermissionsView, self).get_context_data(**kwargs)
        self.clear_page_session()

        candidates = self.get_all_candidates()
        experts, admins = candidates.get('experts'), candidates.get('admins')
        context.update({'experts': experts, 'admins': admins})

        # Дерево для кандидатов в эксперты
        experts_tree_data = self.get_candidates_tree_data(candidates_data=experts)
        context.update({f'experts_{key}': value for key, value in experts_tree_data.items()})
        context['experts_checked_category'] = self.request.session.get('experts_checked_category')

        # Дерево для кандидатов в руководители
        admins_tree_data = self.get_candidates_tree_data(candidates_data=admins)
        context.update({f'admins_{key}': value for key, value in admins_tree_data.items()})
        context['admins_checked_category'] = self.request.session.get('admins_checked_category')

        # Блок кандидатов в руководители
        search_result = None
        if editor_last_name := self.request.GET.get('editor_last_name'):
            search_result = User.objects.filter(last_name__icontains=editor_last_name)
            context['editor_last_name'] = editor_last_name
        context['editors'] = User.objects.order_by('first_name') if not search_result else search_result
        context['last_set_editors'] = self.request.session.get('last_set_editors')
        return context


@require_http_methods(["POST"])
def set_users_as_editor(request):
    """
        Назначить права редактора пользователям
    """
    users_pk = [int(elm.replace('editor_', '')) for elm in request.POST.keys() if elm != 'csrfmiddlewaretoken']
    # Если после повторного сохранения пользователя нет в списке редакторов,
    # которые получили права в рамках текущей сессии, то снимаем с них права редакторов
    if request.session.get('last_set_editors'):
        unset_editor_perm = [user_pk for user_pk in request.session.get('last_set_editors') if user_pk not in users_pk]
        if unset_editor_perm:
            users_for_unset_perm = User.objects.filter(pk__in=unset_editor_perm, is_redactor=True)
            updated_users = list()
            for user in users_for_unset_perm:
                user.is_redactor = False
                updated_users.append(user)
            User.objects.bulk_update(updated_users, ['is_redactor'])

            updated_permissions = list()
            for user in users_for_unset_perm:
                user_permissions, _ = SpecialPermissions.objects.get_or_create(expert=user)
                user_permissions.editor = False
                updated_permissions.append(user_permissions)
            SpecialPermissions.objects.bulk_update(updated_permissions, ['editor'])
            for user in updated_users:
                request.session['last_set_editors'].remove(user.pk)

    if not users_pk:
        return redirect('special_permissions_page')

    users = User.objects.filter(pk__in=users_pk, is_redactor=False)
    if not users.exists():
        return redirect('special_permissions_page')

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

    # Сохраняем данные о назначенных редакторах за текущую сессию
    if session_data := request.session.get('last_set_editors'):
        request.session['last_set_editors'] += [user.pk for user in updated_users if user.pk not in session_data]
    else:
        request.session['last_set_editors'] = [user.pk for user in updated_users]
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

    # Сохраняем данные о категориях в которых были выданы права эксперта за текущую сессию
    if request.session.get('experts_checked_category'):
        request.session['experts_checked_category'].append(category_pk)
    else:
        request.session['experts_checked_category'] = [category_pk]
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
                preknowledge_count, knowledge_count, expertise_count = user_data['categories'][category.pk]
                candidates_by_category.append(
                    (user_pk, user.get_full_name(), preknowledge_count, knowledge_count, expertise_count)
                )
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

    # Сохраняем данные о категориях в которых были выданы права руководителя за текущую сессию
    if request.session.get('admins_checked_category'):
        request.session['admins_checked_category'].append(category_pk)
    else:
        request.session['admins_checked_category'] = [category_pk]
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
            Метод для получения данных о кол-ве созданных знаний, экспертиз и предзнаний
            пользователя в рамках той или иной компетенции (категории)
            Результирующие данные:
            {
            <int:category_pk>:
            {knowledge_count: <int:count>, expertise_count: <int:count>, 'preknowledge_count': <int:count>}...
            }
        """
        return {
            category: {
                'knowledge_count': knowledge_count,
                'expertise_count': expertise_count,
                'preknowledge_count': preknowledge_count
            }
            for category, (knowledge_count, expertise_count, preknowledge_count) in all_competencies_data.items()
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
        if permissions.editor:
            context['edit_knowledge_count'] = Znanie.objects.filter(redactor_id=user_pk).count()

        # Получение данных по компетенциям пользователя как руководителя
        admin_competencies = permissions.admin_competencies.values_list('pk', flat=True)
        context['admin_comp'] = self.get_competencies_data_by_categories(admin_competencies, competencies_data)
        context['admins_nodes'] = self.get_user_permissions_tree_data(competencies_data=context['admin_comp'])
        context['permissions'] = permissions
        return context


class ExpertCandidateKnowledgeView(TemplateView, CandidatesMixin):
    """
        Страница со списком знаний, которые были созданы кандидатом в эксперты в рамках определённой компетенции
    """
    template_name = 'drevo/special_permissions_page/candidate_knowledge_page.html'

    def get_context_data(self, **kwargs):
        context = super(ExpertCandidateKnowledgeView, self).get_context_data(**kwargs)
        candidate_pk = self.kwargs.get('candidate_pk')
        category_pk = self.kwargs.get('category_pk')
        context['candidate'] = get_object_or_404(User, pk=candidate_pk)
        knowledge_data = self.get_expert_candidate_knowledge(candidate_pk=candidate_pk, category_pk=category_pk)
        context['knowledge_data'] = knowledge_data
        context['backup_url'] = reverse('experts_candidates_page', kwargs={'category_pk': category_pk})
        context['page_title'] = f'Список знаний кандидата в эксперты: {context["candidate"].get_full_name()}'
        return context


class AdminCandidateKnowledgeView(TemplateView, CandidatesMixin):
    """
        Страница со списком знаний, которые были созданы кандидатом в руководители в рамках определённой компетенции
    """
    template_name = 'drevo/special_permissions_page/candidate_knowledge_page.html'

    def get_context_data(self, **kwargs):
        context = super(AdminCandidateKnowledgeView, self).get_context_data(**kwargs)
        candidate_pk = self.kwargs.get('candidate_pk')
        category_pk = self.kwargs.get('category_pk')
        context['candidate'] = get_object_or_404(User, pk=candidate_pk)
        knowledge_data = self.get_admin_candidate_knowledge(candidate_pk=candidate_pk, category_pk=category_pk)
        context['knowledge_data'] = knowledge_data
        context['backup_url'] = reverse('admins_candidates_page', kwargs={'category_pk': category_pk})
        context['page_title'] = f'Список знаний кандидата в руководители: {context["candidate"].get_full_name()}'
        return context
