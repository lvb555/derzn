from django.shortcuts import render
from django.http import JsonResponse
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
from users.models import User


def editorial_staff_view(request):
    users = User.objects.all().order_by('last_name')
    template_name = 'admin/drevo/knowledge/editorial_staff_template.html'
    return render(request, template_name, {'users': users})






@csrf_exempt
def update_roles(request):
    if request.method == 'POST':
        user_id = request.POST.get('userId')
        # Преобразование строк 'true'/'false' в булевы значения True/False
        is_employee = request.POST.get('isEmployee') == 'true'
        is_admin = request.POST.get('isAdmin') == 'true'

        try:
            user = User.objects.get(id=user_id)
            user.is_staff = is_employee
            user.is_superuser = is_admin
            user.save()
            return JsonResponse({'message': 'Roles updated successfully'})
        except User.DoesNotExist:
            return JsonResponse({'error': 'User does not exist'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)

