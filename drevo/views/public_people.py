from django.shortcuts import render, get_object_or_404
from users.models import User, MenuSections
from django.db.models.functions import Lower


def public_people_view(request):
    context = {'public_people': []}
    public_people = User.objects.filter(is_public=True).order_by(Lower('last_name').desc())
    context['public_people'] = public_people
    template_name = 'drevo/public_people.html'

    return render(request, template_name, context)

def public_human(request,id):
    context = {'pub_user': [], 'sections': []}
    user = User.objects.get(id=id)
    context['pub_user'] = user
    context['sections'] = [i.name for i in user.sections.all()]
    context['activity'] = [i.name for i in user.sections.all() if i.name.startswith('Мои') or i.name.startswith('Моя')]
    template_name = 'drevo/public_human.html'
    return render(request, template_name, context)