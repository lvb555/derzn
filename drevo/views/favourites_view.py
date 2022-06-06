from django.views import View
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin

from drevo.relations_tree import get_knowledges_by_categories

from users.models import Favourite


class FavouritesView(LoginRequiredMixin, View):
    """
    Выводит избранное
    """

    def get(self, request):
        knowledges = categories = None

        user_favourites = Favourite.objects.filter(user=request.user)
        if user_favourites.exists():
            categories, knowledges = get_knowledges_by_categories(
                user_favourites.first().favourites.filter(is_published=True)
            )

        context = {'knowledges': knowledges, 'categories': categories}
        return render(request, 'drevo/favourites.html', context=context)
