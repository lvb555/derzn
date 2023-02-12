from django.shortcuts import render, redirect
import json
from drevo.models import Category
from users.models import MenuSections, User


def sub_by_category(request, id):
    if request.method == 'GET':
        user = User.objects.filter(id=id).first()
        context = {}
        if user is not None:
            context['categories'] = Category.objects.all()
            if user == request.user:
                context['sections'] = [i.name for i in MenuSections.objects.all()]
                context['activity'] = [i.name for i in MenuSections.objects.all() if i.name.startswith('Мои') or
                            i.name.startswith('Моя')]
                context['link'] = 'users:myprofile'
            else:
                context['sections'] = [i.name for i in user.sections.all()]
                context['activity'] = [i.name for i in user.sections.all() if i.name.startswith('Мои') or i.name.startswith('Моя')]
                context['link'] = 'public_human'
                context['id'] = id
            context['pub_user'] = user
            return render(request, 'drevo/category_subscription.html', context)

    if request.method == 'POST':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Данные с фронта {'Война в Донбассе': True, 'Грамматика': False}
            subscribed_to_category = json.loads(request.body)
            category_subscribed_to = Category.objects.filter(
                name__in=subscribed_to_category)

            for category in category_subscribed_to:
                if subscribed_to_category[category.name]:
                    category.subscribers.add(request.user)
                elif not subscribed_to_category[category.name]:
                    category.subscribers.remove(request.user)

        return redirect('subscription_by_category',id=id)
