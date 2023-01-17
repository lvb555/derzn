from django.shortcuts import render
from users.models import User
from django.db.models.functions import Lower


def public_people_view(request):
    context = {'public_people': []}
    public_people = User.objects.filter(is_public=True).order_by(Lower('last_name').desc())
    context['public_people'] = public_people
    template_name = 'drevo/public_people.html'

    return render(request, template_name, context)
