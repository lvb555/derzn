from django.db.models import Count, F
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView

from api.category_knowledge_serializers import CategorySerializer, KnowledgeSerializer
from drevo.models import Category, Znanie

published_map = {"all": None, "yes": True, "no": False}


class FakeQuerySet:
    def __init__(self, total_size):
        self._total_size = total_size
        self._offset = 0
        self._limit = total_size

    def count(self):
        return self._total_size

    def __len__(self):
        return min(self._limit, self._total_size - self._offset)

    def __getitem__(self, key):
        if isinstance(key, slice):
            new_qs = self.__class__(self._total_size)
            new_qs._offset = self._offset + (key.start or 0)
            new_qs._limit = (key.stop or self._total_size) - (key.start or 0)
            return new_qs
        raise TypeError("Индексирование не поддерживается")

    def __iter__(self):
        # Заглушка для итерации
        for i in range(len(self)):
            yield None


class CustomPagination(PageNumberPagination):
    page_size = 100  # Количество элементов на странице
    page_size_query_param = "page_size"  # Параметр для изменения размера страницы
    max_page_size = 200  # Максимальный размер страницы

    def get_page_values(self, request):
        page_size = self.get_page_size(request)
        page_number = int(request.query_params.get(self.page_query_param, 1))
        if page_number in self.last_page_strings:
            page_number = float("inf")
        return page_number, page_size

    def paginate_dual(self, request, category_queryset, knowledge_queryset):
        page_number, page_size = self.get_page_values(request)
        # print(f'{page_number=} {page_size=}')
        # надо получить полные размеры, иначе непонятно сколько страниц
        category_count = category_queryset.count()
        knowledge_count = knowledge_queryset.count()

        # я не знаю что еще придумать чтобы без велосипеда работала пагинация
        fake_qs = FakeQuerySet(category_count + knowledge_count)
        self.paginate_queryset(fake_qs, request)

        offset = (page_number - 1) * page_size
        limit = page_size
        end = limit + offset
        # print(f'{offset} {end} {category_count} {knowledge_count}')
        qs1_pair = None
        qs2_pair = None

        if end <= category_count:
            # берем только из категорий
            qs1_pair = (offset, end)

        elif offset >= category_count:
            # берем только из знаний
            offset -= category_count
            if offset < knowledge_count:
                end = min(offset + limit, knowledge_count)
                qs2_pair = (offset, end)
        else:
            # берем из категорий и остаток из знаний
            end1 = category_count
            qs1_pair = (offset, end1)

            offset = 0
            limit = end - category_count
            end2 = min(offset + limit, knowledge_count)
            qs2_pair = (offset, end2)

        qs1 = [] if qs1_pair is None else category_queryset[qs1_pair[0] : qs1_pair[1]]
        qs2 = [] if qs2_pair is None else knowledge_queryset[qs2_pair[0] : qs2_pair[1]]
        return qs1, qs2


class CategoryChildrenAPIView(APIView):
    pagination_class = CustomPagination

    def get(self, request, pk=None):

        included_uncategorized = request.query_params.get("include_uncategorized", "no").lower() == "yes"
        filter_published = published_map.get(request.query_params.get("published", "yes").lower())
        filter_system = published_map.get(request.query_params.get("system", "no").lower())

        paginator = self.pagination_class()
        page, page_size = paginator.get_page_values(request)

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
                queryset = queryset.annotate(
                    knowledge_count=Count("znanie", distinct=True), children_count=Count("children", distinct=True)
                )
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
                    "knowledge_count": set_filters(Znanie.objects).filter(category=None).count(),
                }

        # Пагинация
        # paginator = self.pagination_class()

        # устанавливаем фильтры
        sub_category = set_filters(sub_category)
        sub_knowledge = set_filters(sub_knowledge)

        # аннотации для пагинации
        sub_category = optimize_queryset(sub_category)
        sub_knowledge = optimize_queryset(sub_knowledge)

        paginated_categories, paginated_knowledge = paginator.paginate_dual(request, sub_category, sub_knowledge)

        result_categories = CategorySerializer(paginated_categories, many=True).data
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
