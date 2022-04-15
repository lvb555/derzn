import urllib
from django.urls import reverse_lazy
from ..forms import *
from django.views.generic.edit import FormView
from ..models import *
from django.core.paginator import Paginator
from django.db.models import (Q,
                              QuerySet)


class KnowledgeSearchView(FormView):
    template_name = "drevo/knowledge_search.html"
    form_class = KnowledgeSearchForm
    success_url = reverse_lazy("knowledge_search")

    def get_parameters_string(self, include_params: list[str] = None, exclude_params: list[str] = None):
        if include_params and include_params:
            raise Exception('Указаны и включаемые и исключаемые параметры')

        parameters = dict()
        if include_params:
            for parameter, value in self.request.GET.items():
                if parameter in include_params:
                    parameters[parameter] = value
        elif exclude_params:
            for parameter, value in self.request.GET.items():
                if parameter not in exclude_params:
                    parameters[parameter] = value

        return urllib.parse.urlencode(parameters)

    def get_knowledges_with_filter(self,
                                   main_search_parameter=None,
                                   knowledge_type_parameter=None,
                                   knowledge_category_parameter=None,
                                   author_parameter=None,
                                   edge_kind_parameter=None):

        def get_queryset(input_queryset: QuerySet,
                         fields_name: list[str],
                         parameter_value: str,
                         lookup: str = '',
                         connector='AND'):

            if not isinstance(fields_name, list):
                fields_name = [fields_name]

            result_query = Q()
            # Так как sqlite не может искать без учета регистра,
            # будем искать и с заглавной буквы и с маленькой
            for field_name in fields_name:
                query = Q(
                    **{field_name + lookup: parameter_value})

                if not parameter_value.istitle():
                    query = query.__or__(Q(
                        **{field_name + lookup: parameter_value.capitalize()}))

                query_upper = Q(
                    **{field_name + lookup: parameter_value.upper()})

                query_lower = Q(
                    **{field_name + lookup: parameter_value.lower()})

                query = (query.__or__(query_upper)
                         .__or__(query_lower))

                if connector == 'AND':
                    result_query = result_query.__and__(query)
                elif connector == 'OR':
                    result_query = result_query.__or__(query)
                else:
                    raise Exception(f'Некорректный коннектор {connector}')

            outpur_queryset = input_queryset.filter(result_query)
            return outpur_queryset

        knowledges = Znanie.objects.all()
        if main_search_parameter:
            # Ищем знания по главному полю
            knowledges = get_queryset(input_queryset=knowledges,
                                      fields_name=['name',
                                                   'content',
                                                   'source_com', ],
                                      parameter_value=main_search_parameter,
                                      lookup='__contains',
                                      connector='OR')

        if knowledge_type_parameter:
            # Ищем знания по виду знаний
            knowledges = get_queryset(input_queryset=knowledges,
                                      fields_name='tz__name',
                                      parameter_value=knowledge_type_parameter)

        if knowledge_category_parameter:
            # Ищем знания по категории знания
            knowledges = get_queryset(input_queryset=knowledges,
                                      fields_name='category__name',
                                      parameter_value=knowledge_category_parameter)

        if author_parameter:
            # Ищем знания по автору знания
            knowledges = get_queryset(input_queryset=knowledges,
                                      fields_name='author__name',
                                      parameter_value=author_parameter)

        if edge_kind_parameter:
            # Ищем знания по виду связи к знанию
            knowledges = get_queryset(input_queryset=knowledges,
                                      fields_name='related__tr__name',
                                      parameter_value=edge_kind_parameter)

        return knowledges

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Поиск знаний'
        main_search_parameter = self.request.GET.get('main_search')
        knowledge_type_parameter = self.request.GET.get('knowledge_type')
        knowledge_category_parameter = self.request.GET.get(
            'knowledge_category')
        author_parameter = self.request.GET.get('author')
        edge_kind_parameter = self.request.GET.get('edge_kind')

        # Для сохранения любого пользовательского ввода в форме
        context['form'] = KnowledgeSearchForm(self.request.GET)

        if (main_search_parameter
            or knowledge_type_parameter
            or knowledge_category_parameter
            or author_parameter
                or edge_kind_parameter):

            # Для соединение с параметрами пагинации
            context['search_string_parameters'] = self.get_parameters_string(
                exclude_params=['page'])

            knowledges = self.get_knowledges_with_filter(
                main_search_parameter=main_search_parameter,
                knowledge_type_parameter=knowledge_type_parameter,
                knowledge_category_parameter=knowledge_category_parameter,
                author_parameter=author_parameter,
                edge_kind_parameter=edge_kind_parameter
            )

            knowledges = knowledges.select_related(
                'author', 'tz', 'category').prefetch_related('related__tr')

            paginator = Paginator(knowledges, 10)

            cur_page_number = self.request.GET.get('page')

            page_obj = paginator.get_page(cur_page_number)

            context['paginator'] = paginator
            context['page_obj'] = page_obj

        return context
