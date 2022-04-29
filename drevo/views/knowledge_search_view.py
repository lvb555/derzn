import urllib
from django.urls import reverse_lazy
from ..forms import *
from django.views.generic.edit import FormView
from ..models import *
from django.core.paginator import Paginator
from django.db.models import (Q,
                              QuerySet,
                              Count)
from .search_engine import SearchEngineMixin


class KnowledgeSearchView(FormView, SearchEngineMixin):
    template_name = "drevo/search.html"
    form_class = KnowledgeSearchForm
    success_url = reverse_lazy("search_knowledge")

    def get_published_knowledges_with_filter(self,
                                             main_search_parameter=None,
                                             knowledge_type_parameter=None,
                                             knowledge_category_parameter=None,
                                             author_parameter=None,
                                             edge_kind_parameter=None):
        knowledges = (Znanie.objects.filter(is_published=True)
                      .order_by('name')
                      .select_related('author', 'tz', 'category')
                      .prefetch_related('related__tr'))

        result_knowledges = []
        exclude_query_main_search = None
        if main_search_parameter:
            # Ищем знания по главному полю
            # Вначале необходимо получить наборы слов в виде общего списка
            # После чего беру набор и ищу через или
            parameter_value_combinations = self.get_parameter_combinations(
                main_search_parameter)
            combination_queries = []
            for combination in parameter_value_combinations:
                query_previously = None
                for value in combination:
                    query = Q(name__contains=value)
                    query = query | Q(content__contains=value)
                    query = query | Q(source_com__contains=value)

                    if value != value.upper():
                        query = query | Q(name__contains=value.upper())
                        query = query | Q(content__contains=value.upper())
                        query = query | Q(source_com__contains=value.upper())

                    if value != value.lower():
                        query = query | Q(name__contains=value.lower())
                        query = query | Q(content__contains=value.lower())
                        query = query | Q(source_com__contains=value.lower())

                    if query_previously:
                        query = query & query_previously

                    query_previously = query

                if not exclude_query_main_search:
                    combination_queries.append(query)
                    exclude_query_main_search = ~query
                else:
                    combination_queries.append(
                        query & exclude_query_main_search)
                    exclude_query_main_search = exclude_query_main_search & ~query

            for query in combination_queries:
                knowledges_tmp = knowledges.filter(query)
                result_knowledges.extend(list(knowledges_tmp))

        result_query = None
        if knowledge_type_parameter:
            # Ищем знания по виду знаний
            query = self.get_query(fields_name='tz__name',
                                   parameter_value=knowledge_type_parameter)
            if not result_query:
                result_query = query
            else:
                result_query = result_query | query

        if knowledge_category_parameter:
            # Ищем знания по категории знания
            query = self.get_query(fields_name='category__name',
                                   parameter_value=knowledge_category_parameter)
            if not result_query:
                result_query = query
            else:
                result_query = result_query | query

        if author_parameter:
            # Ищем знания по автору знания
            query = self.get_query(fields_name='author__name',
                                   parameter_value=author_parameter)
            if not result_query:
                result_query = query
            else:
                result_query = result_query | query

        if edge_kind_parameter:
            # Ищем знания по виду связи к знанию
            query = self.get_query(fields_name='related__tr__name',
                                   parameter_value=edge_kind_parameter)
            if not result_query:
                result_query = query
            else:
                result_query = result_query | query

        if result_query:
            knowledges = knowledges.filter(
                result_query & exclude_query_main_search)

            result_knowledges.extend(list(knowledges))

        return result_knowledges

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
        # breakpoint()

        if (main_search_parameter
            or knowledge_type_parameter
            or knowledge_category_parameter
            or author_parameter
                or edge_kind_parameter):

            # Для соединение с параметрами пагинации
            context['search_string_parameters'] = self.get_parameters_string(
                exclude_params=['page'])

            knowledges = self.get_published_knowledges_with_filter(
                main_search_parameter=main_search_parameter,
                knowledge_type_parameter=knowledge_type_parameter,
                knowledge_category_parameter=knowledge_category_parameter,
                author_parameter=author_parameter,
                edge_kind_parameter=edge_kind_parameter
            )

            paginator = Paginator(knowledges, 10)

            cur_page_number = self.request.GET.get('page')

            page_obj = paginator.get_page(cur_page_number)

            context['paginator'] = paginator
            context['page_obj'] = page_obj

        return context
