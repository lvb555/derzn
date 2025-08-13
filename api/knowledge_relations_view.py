from django.db.models import Count, Prefetch
from rest_framework import generics
from drevo.models import Znanie, Relation
from api.knowledge_relation_serializers import KnowledgeRelationsSerializer


class KnowledgeRelationsAPIView(generics.RetrieveAPIView):
    #queryset = Znanie.objects.select_related('tz').annotate(relations_count=Count('base'))
    serializer_class = KnowledgeRelationsSerializer
    lookup_field = 'id'

    def get_queryset(self):
        return Znanie.objects.annotate(
            relations_count=Count('base')
        ).prefetch_related(
            Prefetch('base',
                     queryset=Relation.objects.select_related('rz', 'tr').annotate(
                         rz_related_count=Count('rz__base')
                     ),
                     to_attr='prefetched_relations'
                     )
        ).select_related('tz')
