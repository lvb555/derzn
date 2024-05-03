import json

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import JsonResponse
from users.models import User, Profile
from drevo.sender import send_email
from drevo.models.special_permissions import SpecialPermissions
from django.contrib.auth.models import Group, Permission


@login_required
def editorial_staff_view(request):
    if request.user.is_superuser:
        users = User.objects.all().order_by('last_name')
        all_groups = Group.objects.all()

        special_permissions = SpecialPermissions.objects.all().select_related('expert')
        experts = special_permissions.values_list('expert_id', flat=True)

        template_name = 'admin/drevo/knowledge/editorial_staff_template.html'

        return render(request, template_name, {'users': users,
                                               'special_permissions': special_permissions,
                                               'experts': experts,
                                               'all_groups': all_groups})
    else:
        return redirect(request.META['HTTP_REFERER'])


@login_required
def update_roles(request):
    if not request.user.is_superuser or not request.method == 'POST':
        return JsonResponse({'error': 'Invalid request'}, status=400)

    user_id = request.POST.get('userId')
    is_employee = request.POST.get('isEmployee') == 'true'
    is_admin = request.POST.get('isAdmin') == 'true'
    user = User.objects.get(id=user_id)
    message = f'Уважаемый {user.first_name} {user.patronymic}! \n'
    was_admin = user.is_superuser

    if is_employee and is_admin:
        user.is_employee = True
        user.is_superuser = True
        message += "Вам дано право Администратора портала."
        subject = "Дано право Администратора портала"
    elif is_employee:
        user.is_employee = True
        user.is_superuser = False
        if was_admin:
            message += "Вы лишены права Администратора портала."
            subject = "Лишение права Администратора портала"
        else:
            message += "Вам дано право Сотрудника редакции."
            subject = "Дано право Сотрудника редакции"
    else:
        user.is_employee = False
        user.is_superuser = False
        message += "Вы лишены права Сотрудника редакции"
        subject = "Лишение права Сотрудника редакции."

    message += '\n\nРедакция портала "Дерево знаний" '
    user.save()

    send_email(user.email, subject, False, message)

    return JsonResponse({'message': 'Roles updated successfully'})





@login_required
def update_user_permissions(request):
    if not request.user.is_superuser or not request.method == 'POST':
        return JsonResponse({'error': 'Invalid request'}, status=400)
    data = json.loads(request.body)
    user_id = data.get('userId')
    group = Group.objects.get(name=data.get('group'))
    granted = data.get('granted')

    user = User.objects.get(id=user_id)
    permissions = Permission.objects.filter(group=group)

    if granted:
        user.groups.add(group)
        user.user_permissions.add(*permissions)
    else:
        user.groups.remove(group)
        user.user_permissions.remove(*permissions)
    return JsonResponse({'message': 'permissions updated successfully'})

