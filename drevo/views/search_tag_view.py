from django.urls import reverse_lazy
from ..forms import *
from django.views.generic.edit import FormView
from ..models import *
from django.core.paginator import Paginator
from django.db.models import (Q,
                              QuerySet,
                              Count,
                              Value)
from django.forms import formset_factory
from .search_engine import SearchEngineMixin
from .search_knowledge_view import KnowledgeSearchView


class TagSearchView(FormView, SearchEngineMixin):
    template_name = "drevo/search_tag.html"
    form_class = TagSearchForm
    success_url = reverse_lazy("search_tag")

    def get_published_tags_with_filter(self,
                                       main_search_parameter=None,
                                       ):

        tags = (Label.objects
                .annotate(published_knowledges=Count(
                    'znanie',
                    filter=Q(znanie__is_published=True))
                )
                .filter(znanie__gt=0)
                .order_by('name'))

        # Ищем теги по главному полю
        # Вначале необходимо получить наборы слов в виде общего списк
        # После чего беру набор и ищу через или
        parameter_value_combinations = self.get_parameter_combinations(
            main_search_parameter)
        exclude_query = None
        combination_queries = []
        for combination in parameter_value_combinations:
            query_previously = None
            for value in combination:
                query = Q(name__contains=value)

                if value != value.upper():
                    query = query | Q(name__contains=value.upper())

                if value != value.lower():
                    query = query | Q(name__contains=value.lower())

                if value != value.capitalize():
                    query = query | Q(name__contains=value.capitalize())

                if query_previously:
                    query = query & query_previously

                query_previously = query

            if not exclude_query:
                combination_queries.append(query)
                exclude_query = ~query
            else:
                combination_queries.append(query & exclude_query)
                exclude_query = ~query & exclude_query

        tags_list = []
        for query in combination_queries:
            tags_tmp = tags.filter(query)
            tags_list.extend(list(tags_tmp))

        return tags_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Поиск тегов'
        main_search_parameter = self.request.GET.get('main_search')

        tag_parameters = KnowledgeSearchView.get_tag_names(self.request)
        context['tag_formset'] = KnowledgeSearchView.get_tag_formset(
            self.request)
        if tag_parameters and not context['tag_formset'].is_valid():
            return context
        # Для сохранения любого пользовательского ввода в форме
        context['form'] = TagSearchForm(self.request.GET)

        if main_search_parameter:

            # Для соединение с параметрами пагинации
            context['search_string_parameters'] = self.get_parameters_string(
                exclude_params=['page'])

            tags = self.get_published_tags_with_filter(
                main_search_parameter=main_search_parameter,
            )

            paginator = Paginator(tags, 10)

            cur_page_number = self.request.GET.get('page')

            page_obj = paginator.get_page(cur_page_number)

            context['paginator'] = paginator
            context['page_obj'] = page_obj

        return context
