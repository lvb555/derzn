from django.db.models import Count, F
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView

from api.serializers import CategorySerializer, KnowledgeSerializer
from drevo.models import Category, Znanie

published_map = {"all": None, "yes": True, "no": False}


class CustomPagination(PageNumberPagination):
    page_size = 100  # Количество элементов на странице
    page_size_query_param = "page_size"  # Параметр для изменения размера страницы
    max_page_size = 200  # Максимальный размер страницы


class CategoryChildrenAPIView(APIView):
    pagination_class = CustomPagination

    def get(self, request, pk=None):

        included_uncategorized = request.query_params.get("include_uncategorized", "no").lower() == "yes"
        filter_published = published_map.get(request.query_params.get("published", "yes").lower())
        filter_system = published_map.get(request.query_params.get("system", "no").lower())

        page = int(request.query_params.get("page", 1))

        uncategorized_record = None
        sub_knowledge = Znanie.objects.none()
        sub_category = Category.objects.none()

        def set_filters(queryset):
            # устанавливаем фильтры согласно параметрам
            if filter_published is not None:
                queryset = queryset.filter(is_published=filter_published)
            if queryset.model == Znanie and filter_system is not None:
                queryset = queryset.filter(tz__is_systemic=filter_system)
            return queryset.order_by("name")

        def optimize_queryset(queryset):
            if queryset.model == Znanie:
                queryset = (
                    queryset.select_related("tz", "author")  # Для type_name и type_icon  # Для author_name
                    .only("id", "name", "tz__name", "author__name")  # Для type_name и type_icon  # Для author_name
                    .annotate(type_name=F("tz__name"), author_name=F("author__name"))
                )
            elif queryset.model == Category:
                queryset = queryset.annotate(knowledge_count=Count("znanie"), children_count=Count("children"))
            return queryset

        if pk == "uncategorized":  # Специальный случай для знаний без категории
            sub_knowledge = Znanie.objects.filter(category=None)

        elif pk:  # Дочерние элементы конкретной категории
            category = Category.objects.get(pk=pk)
            sub_category = category.get_children()
            sub_knowledge = Znanie.objects.filter(category=category)

        else:  # Корневые категории
            sub_category = Category.objects.filter(parent=None)
            # Добавляем категорию "Знания без категории" только если это первая страница
            if included_uncategorized and page == 1:
                uncategorized_record = {
                    "id": "uncategorized",
                    "name": "Знания без категории",
                    "children_count": 0,
                    "knowledge_count": Znanie.objects.filter(category=None).count(),
                }

        # Пагинация
        paginator = self.pagination_class()
        result_categories = []
        result_knowledge = []

        # устанавливаем фильтры
        sub_category = set_filters(sub_category)
        sub_knowledge = set_filters(sub_knowledge)

        # аннотации для пагинации
        sub_category = optimize_queryset(sub_category)
        sub_knowledge = optimize_queryset(sub_knowledge)

        if sub_category.exists():

            paginated_categories = paginator.paginate_queryset(sub_category, request)
            result_categories = CategorySerializer(paginated_categories, many=True).data

        if sub_knowledge.exists():
            paginated_knowledge = paginator.paginate_queryset(sub_knowledge, request)
            result_knowledge = KnowledgeSerializer(paginated_knowledge, many=True).data

        # Добавляем категорию "Знания без категории"
        if uncategorized_record:
            result_categories.insert(0, uncategorized_record)

        return paginator.get_paginated_response(
            {
                "categories": result_categories,
                "knowledge": result_knowledge,
            }
        )
