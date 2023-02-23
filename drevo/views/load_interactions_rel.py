from ..models.relation_type import Tr
from ..models.interconnections_of_relations import AllowedRelationCombinations
from ..models.relation_type import Tr

from dal import autocomplete


class RelationAutocomplete(autocomplete.Select2QuerySetView):
    
    def get_queryset(self):
        knowledge = self.forwarded.get('bz', None)
        qs = Tr.objects.all()

        return knowledge
        
        # if knowledge:
        #     allowed_combinations = InteractionsOfRelations.objects.filter(base_knowledge_type=knowledge.tz)
        #     print(allowed_combinations)
        #     relation_types = Tr.objects.all()
        
        #     for type in relation_types:
        #         if type in allowed_combinations:
        #             qs.append(type)
        #     print(qs)
        # else:
        #     qs = Tr.objects.all()
        # return qs
        

