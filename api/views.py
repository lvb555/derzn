from rest_framework.views import APIView
from rest_framework.response import Response
from drevo.models import Category, Znanie
from api.serializers import CategorySerializer, KnowledgeSerializer

published_map = {
    'all': None,
    'yes': True,
    'no': False
}


class CategoryChildrenAPIView(APIView):
    def get(self, request, pk=None):

        included_uncategorized = request.query_params.get('include_uncategorized', 'no').lower() == 'yes'
        filter_published = published_map.get(request.query_params.get('published', 'yes').lower())
        filter_system = published_map.get(request.query_params.get('system', 'no').lower())
        uncategorized_record = None

        def set_filters(queryset):
            if filter_published is not None:
                queryset = queryset.filter(is_published=filter_published)
            if queryset.model == Znanie and filter_system is not None:
                queryset = queryset.filter(tz__is_systemic=filter_system)
            return queryset

        if pk == 'uncategorized':  # Специальный случай для знаний без категории
            knowledge_qs = set_filters(Znanie.objects.filter(category=None))
            return Response({
                'knowledge': KnowledgeSerializer(knowledge_qs, many=True).data,
            })

        if pk:  # Дочерние элементы конкретной категории
            category = Category.objects.get(pk=pk)
            children = set_filters(category.get_children())
            knowledge = set_filters(Znanie.objects.filter(category=category))

        else:  # Корневые категории
            children = set_filters(Category.objects.filter(parent=None))
            knowledge = Znanie.objects.none()

            if included_uncategorized:
                uncategorized_record = {"id": "uncategorized", "name": "Знания без категории", "children_count": 0,
                                        "knowledge_count": Znanie.objects.filter(category=None).count()}

        categories = CategorySerializer(children, many=True).data
        if uncategorized_record:
            categories.insert(0, uncategorized_record)

        return Response({
            'categories': categories,
            'knowledge': KnowledgeSerializer(knowledge, many=True).data,
            'count': children.count()
        })
