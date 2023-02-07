from ..models.knowledge_kind import Tz
from ..models.knowledge import Znanie
from ..models.relation_type import Tr
from ..models.interconnections_of_relations import InteractionsOfRelations
from ..models.relation_type import Tr

from ..forms.relation_form import RelationAdminForm

from django.shortcuts import render

from django.http import JsonResponse

from dal import autocomplete

 
class KnowledgeAutocomplete(autocomplete.Select2QuerySetView):
    """
    View который фильтрует объекты модели Знание на основе выбранного вида связи
    И видов знания, подходящих для вида связи
    """

    def get_queryset(self):
        
        #qs = Znanie.objects.all()
        qs = []

        rel_type = self.forwarded.get('tr', None)

        if rel_type:
            qs = Znanie.objects.all()
            allowed_combinations = InteractionsOfRelations.objects.filter(relation_type=rel_type)
            for knowledge in qs:
                if knowledge.tz in allowed_combinations:
                    qs.append(knowledge)
            print(qs)
        elif self.q:
            qs = None#qs.filter(bz__name=self.q)#Znanie.objects.all() 
        return qs


def test_ajax_view(request):
    form = RelationAdminForm
    context = {'form': form}
    return render(request, "drevo/test.html", context)


def test_response(request):
    if request.method == "GET":
        res = {"status": "okkkk"}
    return JsonResponse(res)


def zn_autocomplete(request):
    tr = request.GET.get('tr', None)

    allowed_combinations = InteractionsOfRelations.objects.filter(relation_type=tr)

    qs = Znanie.objects.all()

    for obj in qs:
        pass

    return JsonResponse(qs)




# Example from stackoverflow


# from dal import autocomplete
# from .models import Item


# class ItemAutocompleteView(autocomplete.Sчelect2QuerySetView):

#     def get_queryset(self):
#         if not self.request.user.is_authenticated:
#             return Item.objects.none()

#         shop = self.forwarded.get('shop', None)
#         if shop:
#             qs = Item.objects.filter(shop=shop)
#         else:
#             qs = Item.objects.none()

#         # I assume your Item model has `title` field (this is searchable column. you can search on field value )
#         if self.q:
#             qs = qs.filter(title__istartswith=self.q)

#         return qs


# Example from docs

# class CountryAutocomplete(autocomplete.Select2QuerySetView):
#     def get_queryset(self):
#         if not self.request.user.is_authenticated:
#             return Country.objects.none()

#         qs = Country.objects.all()

#         continent = self.forwarded.get('continent', None)

#         if continent:
#             qs = qs.filter(continent=continent)

#         if self.q:
#             qs = qs.filter(name__istartswith=self.q)

#         return qs