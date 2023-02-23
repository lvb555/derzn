from ..models.knowledge_kind import Tz
from ..models.knowledge import Znanie
from ..models.relation_type import Tr
from ..models.interconnections_of_relations import AllowedRelationCombinations
from ..models.relation_type import Tr

from django.shortcuts import render

from django.http import JsonResponse

from dal import autocomplete

from django.core import serializers

import json, pprint

 
def test_ajax_view(request):
    return render(request, "drevo/test.html", {})


def load_tr(request):
    bz = Znanie.objects.filter(name=request.GET["bz"]).get()
    allowed_tr = AllowedRelationCombinations.objects.filter(base_knowledge_type=bz.tz).values()
    print(allowed_tr)
    allowed_json = {}
    for elem in allowed_tr:
        tr = Tr.objects.filter(id=elem['relation_type_id']).values_list('id', 'name')
        print(tr[0])
        allowed_json[tr[0][1]] = tr[0][0]
    print("-----------------------------")
    print(allowed_json)
    return JsonResponse(allowed_json, safe=False)


def load_bz(requset):
    tr = Tr.objects.filter(name=requset.GET['tr']).get()
    print(tr)
    allowed_bz = AllowedRelationCombinations.objects.filter(relation_type=tr).values()
    print(allowed_bz)
    allowed_json = {}
    for elem in allowed_bz:
        bz = Znanie.objects.filter(id=elem['base_knowledge_type_id']).values_list('id', 'name')
        print(bz[0])
        allowed_json[bz[0][1]] = bz[0][0]
    print("-----------------------------")
    print(allowed_json)
    return JsonResponse(allowed_json, safe=False)

def load_rz(request):
    pass

def zn_autocomplete(request):
    tr = request.GET.get('tr', None)

    allowed_combinations = AllowedRelationCombinations.objects.filter(relation_type=tr)

    qs = Znanie.objects.all()

    for obj in qs:
        pass

    return JsonResponse(qs)


def tr_autocomplete(request):
    
    # zn = request.GET.get('bz', None)

    # allowed_combinations = InteractionsOfRelations.objects.filter(relation_type=tr)

    # qs = Znanie.objects.all()

    # for obj in qs:
    #     pass

    return JsonResponse({})



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