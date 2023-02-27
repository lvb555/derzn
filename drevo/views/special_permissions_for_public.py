from django.shortcuts import redirect, get_object_or_404, render
from drevo.models import Category, SpecialPermissions, Znanie
from drevo.views import UsersSpecialPermissionsView
from users.models import User, MenuSections
from users.views import access_sections


def get_special_permission(request, id):
    user = User.objects.filter(id=id).first()
    context = {}

    users_permissions = UsersSpecialPermissionsView()
    if user is not None:
        if user == request.user:
            context['sections'] = access_sections(user)
            context['activity'] = [i for i in context['sections'] if i.startswith('Мои') or
                                   i.startswith('Моя')]
            context['link'] = 'users:myprofile'
        else:
            context['sections'] = [i.name for i in user.sections.all()]
            context['activity'] = [i.name for i in user.sections.all() if
                                   i.name.startswith('Мои') or i.name.startswith('Моя')]
            context['link'] = 'public_human'
            context['id'] = id
        context['pub_user'] = user
        permissions = SpecialPermissions.objects.prefetch_related('categories', 'admin_competencies').filter(expert=user).first()
        if permissions:
            competencies_data = users_permissions.get_user_competencies_data(user.pk)
            # Получение данных по компетенциям пользователя как эксперта
            expert_competencies = permissions.categories.values_list('pk', flat=True)
            context['expert_comp'] = users_permissions.get_competencies_data_by_categories(expert_competencies, competencies_data)
            context['experts_nodes'] = users_permissions.get_user_permissions_tree_data(competencies_data=context['expert_comp'])

            # Получение данных по работе пользователя как редактора
            if permissions.editor:
                context['edit_knowledge_count'] = Znanie.objects.filter(redactor_id=user.pk).count()

            # Получение данных по компетенциям пользователя как руководителя
            admin_competencies = permissions.admin_competencies.values_list('pk', flat=True)
            context['admin_comp'] = users_permissions.get_competencies_data_by_categories(admin_competencies, competencies_data)
            context['admins_nodes'] = users_permissions.get_user_permissions_tree_data(competencies_data=context['admin_comp'])
            context['permissions'] = permissions
        return render(request, 'drevo/special_permissions_for_public.html', context)
