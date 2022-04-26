import urllib
from django.urls import reverse_lazy
from ..forms import *
from django.views.generic.edit import FormView
from ..models import *
from django.core.paginator import Paginator
from django.db.models import (Q,
                              QuerySet)
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
        knowledges = Znanie.objects.filter(is_published=True)
        result_query = Q()
        if main_search_parameter:
            # Ищем знания по главному полю
            result_query = result_query | self.get_query(fields_name=['name',
                                                                      'content',
                                                                      'source_com', ],
                                                         parameter_value=main_search_parameter,
                                                         lookup='__contains',
                                                         connector='OR')

        if knowledge_type_parameter:
            # Ищем знания по виду знаний
            result_query = result_query | self.get_query(fields_name='tz__name',
                                                         parameter_value=knowledge_type_parameter)

        if knowledge_category_parameter:
            # Ищем знания по категории знания
            result_query = result_query | self.get_query(fields_name='category__name',
                                                         parameter_value=knowledge_category_parameter)

        if author_parameter:
            # Ищем знания по автору знания
            result_query = result_query | self.get_query(fields_name='author__name',
                                                         parameter_value=author_parameter)

        if edge_kind_parameter:
            # Ищем знания по виду связи к знанию
            result_query = result_query | self.get_query(fields_name='related__tr__name',
                                                         parameter_value=edge_kind_parameter)

        knowledges = knowledges.filter(result_query)

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

            knowledges = (knowledges
                          .order_by('name')
                          .select_related('author', 'tz', 'category')
                          .prefetch_related('related__tr'))

            paginator = Paginator(knowledges, 10)

            cur_page_number = self.request.GET.get('page')

            page_obj = paginator.get_page(cur_page_number)

            context['paginator'] = paginator
            context['page_obj'] = page_obj

        return context
