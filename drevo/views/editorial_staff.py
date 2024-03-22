from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from users.models import User, Profile
from drevo.sender import send_email
from drevo.models.special_permissions import SpecialPermissions

def editorial_staff_view(request):
    users = User.objects.all().order_by('last_name')
    special_permissions = SpecialPermissions.objects.all()
    experts = []
    id_experts = special_permissions.values_list('expert', flat=True)

    for i in id_experts:
        experts.append(User.objects.get(id=i))

    template_name = 'admin/drevo/knowledge/editorial_staff_template.html'
    return render(request, template_name, {'users': users,
                                           'special_permissions': special_permissions,
                                           'experts': experts})


@csrf_exempt
def update_roles(request):
    if request.method == 'POST':
        user_id = request.POST.get('userId')
        is_employee = request.POST.get('isEmployee') == 'true'
        is_admin = request.POST.get('isAdmin') == 'true'

        try:
            user = User.objects.get(id=user_id)

            message = f'Уважаемый {user.first_name} {user.profile.patronymic}! \n'
            if is_employee and is_admin:
                user.is_employee = True
                user.is_superuser = True
                message += "Вам дано право Сотрудника редакции и Администратора портала."
                subject = "Дано право Сотрудника редакции и Администратора портала"
            elif is_employee:
                user.is_employee = True
                message += "Вам дано право Сотрудника редакции."
                subject = "Дано право Сотрудника редакции"
            elif is_admin:
                user.is_superuser = True
                message += "Вам дано право Администратора портала."
                subject = "Дано право Администратора портала"
            else:
                user.is_employee = False
                user.is_superuser = False
                message = "Вы лишены всех прав."
                subject = "Лишение всех прав пользователя"

            message += '\nРедакция портала "Дерево знаний" '
            user.save()

            send_email(user.email, subject, False, message)


            return JsonResponse({'message': 'Roles updated successfully'})
        except User.DoesNotExist:
            return JsonResponse({'error': 'User does not exist'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)
