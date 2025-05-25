import re

from django.http import JsonResponse
from django.urls import reverse_lazy
from drevo.models import Category
from drevo.forms import KnowledgeSearchForm
from django.views.generic.edit import FormView
from drevo.models import Znanie
from django.core.paginator import Paginator
from django.db.models import Q
from .search_engine import SearchEngineMixin
from django.forms import formset_factory
from ..models.user_parameters import UserParameters


class MainSearchKnowledge:
    def __init__(self,
                 main_search: str,
                 main_search__name_on: bool = True,
                 main_search__content_on: bool = True,
                 main_search__source_com_on: bool = True):
        self.fields = {}
        self.fields['name'] = main_search__name_on and main_search
        self.fields['content'] = main_search__content_on and main_search
        self.fields['source_com'] = main_search__source_com_on and main_search

    def need_search(self):
        for value in self.fields.values():
            if value:
                return True

    def get_query__contains(self, value, query: Q = None):
        for field_name, value in self.fields.items():
            if not value:
                continue
            query_dict = {f'{field_name}__contains': value}
            if not query:
                query = Q(**query_dict)
            else:
                query = query | Q(**query_dict)

        return query


class KnowledgeSearchView(FormView, SearchEngineMixin):
    template_name = "drevo/search_knowledge.html"
    form_class = KnowledgeSearchForm
    success_url = reverse_lazy("search_knowledge")

    def clean_category(self, knowledge_category: str) -> str:
        return knowledge_category.strip()

    def get_published_knowledges_with_filter(self,
                                             main_search_parameter=None,
                                             knowledge_type_parameter=None,
                                             knowledge_category_parameter=None,
                                             author_parameter=None,
                                             edge_kind_parameter=None,
                                             tag_parameters=None):
        knowledges = (Znanie.objects.filter(is_published=True,
                                            tz__is_systemic=False)
                      .order_by('name')
                      .select_related('author', 'tz', 'category')
                      .prefetch_related('related__tr', 'labels'))

        extra_query = None

        if knowledge_type_parameter:
            # Ищем знания по виду знаний
            query = self.get_query(fields_name='tz__name',
                                   parameter_value=knowledge_type_parameter)

            extra_query = query if not extra_query else extra_query & query

        if knowledge_category_parameter:
            # Ищем знания по категории знания
            category = Category.objects.get(id=knowledge_category_parameter)
            descendants = category.get_descendants()
            query = Q(category=category)
            for descendant in descendants:
                query = query | Q(category=descendant)

            extra_query = query if not extra_query else extra_query & query

        if author_parameter:
            # Ищем знания по автору знания
            query = self.get_query(fields_name='author__name',
                                   parameter_value=author_parameter)

            extra_query = query if not extra_query else extra_query & query

        if edge_kind_parameter:
            # Ищем знания по виду связи к знанию
            query = self.get_query(fields_name='related__tr__name',
                                   parameter_value=edge_kind_parameter)

            extra_query = query if not extra_query else extra_query & query

        if tag_parameters:
            # Ищем знания по виду тегам
            tag_queries = []
            for tag_name in tag_parameters:
                query = self.get_query(fields_name='labels__name',
                                       parameter_value=tag_name)
                tag_queries.append(query)

        if extra_query:
            knowledges = knowledges.filter(extra_query)

        if tag_parameters:
            for query in tag_queries:
                knowledges = knowledges.filter(query)

        exclude_query = None
        if self.main_search_kwowledge.need_search():
            # Ищем знания по главному полю
            # Вначале необходимо получить наборы слов в виде общего списка
            # После чего беру набор и ищу через или
            parameter_value_combinations = self.get_parameter_combinations(
                main_search_parameter)
            combination_queries = []
            for combination in parameter_value_combinations:
                query_previously = None
                for value in combination:
                    value_list = [value, value.upper(), value.lower(), value.capitalize()]
                    for val in value_list:
                        query = self.main_search_kwowledge.get_query__contains(val)

                    if query_previously:
                        query = query & query_previously

                    query_previously = query

                if not exclude_query:
                    combination_queries.append(query)
                    exclude_query = ~query
                else:
                    combination_queries.append(query & exclude_query)
                    exclude_query = ~query & exclude_query

        if main_search_parameter:
            knowledges_list = []
            # Первые запросы в списке соответствуют комбинациям с большим количеством слов
            # Этим добиваемся выдачи вначале знаний с большим совпадением слов
            for query in combination_queries:
                knowledges_tmp = knowledges.filter(query)
                knowledges_list.extend(list(knowledges_tmp))
            return knowledges_list
        return knowledges

    @classmethod
    def get_tag_formset(cls, request):
        tag_factory = formset_factory(KnowledgeSearchForm.Tag, extra=1)
        if 'tags-TOTAL_FORMS' in request.GET:
            tags_dict = {k: v for k, v in request.GET.items()
                         if ('tags' in k) and v}

            tag_formset = tag_factory(
                tags_dict, prefix='tags')

        else:
            tag_formset = tag_factory(prefix='tags')

        return tag_formset

    @classmethod
    def get_tag_names(cls, request):
        RE_TAG = re.compile(r'tags-\d-tag')
        tags = []
        for parameter_name, parameter_value in request.GET.items():
            if RE_TAG.findall(parameter_name) and parameter_value.strip():
                tags.append(parameter_value.strip())
        return tags

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Поиск знаний'
        main_search__name_on = bool(self.request.GET.get('main_search__name'))
        main_search__content_on = bool(self.request.GET.get('main_search__content'))
        main_search__source_com_on = bool(self.request.GET.get('main_search__source_com'))
        main_search_parameter = self.request.GET.get('main_search')
        self.main_search_kwowledge = MainSearchKnowledge(
            main_search_parameter,
            main_search__name_on,
            main_search__content_on,
            main_search__source_com_on
        )
        knowledge_type_parameter = self.request.GET.get('knowledge_type')
        knowledge_category_parameter = self.request.GET.get(
            'knowledge_category')

        author_parameter = self.request.GET.get('author')
        edge_kind_parameter = self.request.GET.get('edge_kind')

        tag_parameters = KnowledgeSearchView.get_tag_names(self.request)

        context['tag_formset'] = KnowledgeSearchView.get_tag_formset(
            self.request)
        # Для сохранения любого пользовательского ввода в форме
        # Валидация формы под капотам класса
        if self.request.GET:
            context['form'] = KnowledgeSearchForm(self.request.GET)
        else:
            context['form'] = KnowledgeSearchForm()

        if tag_parameters and not context['tag_formset'].is_valid():
            return context

        if (self.main_search_kwowledge.need_search()
            or knowledge_type_parameter
            or knowledge_category_parameter
            or author_parameter
            or edge_kind_parameter
                or tag_parameters):

            # Для соединение с параметрами пагинации
            context['search_string_parameters'] = self.get_parameters_string(
                exclude_params=['page'])

            knowledges = self.get_published_knowledges_with_filter(
                main_search_parameter=main_search_parameter,
                knowledge_type_parameter=knowledge_type_parameter,
                knowledge_category_parameter=knowledge_category_parameter,
                author_parameter=author_parameter,
                edge_kind_parameter=edge_kind_parameter,
                tag_parameters=tag_parameters
            )
            user_params = UserParameters.objects.select_related('param').filter(user=self.request.user)
            knowledge_content_length = user_params.filter(
                param__name='Длина поля "Содержание" (слов)'
            ).first().param_value
            context['knowledge_content_length'] = int(knowledge_content_length)
            per_page_value = user_params.filter(
                param__name='Число записей на странице'
            ).first().param_value
            paginator = Paginator(knowledges, int(per_page_value))

            cur_page_number = self.request.GET.get('page')

            page_obj = paginator.get_page(cur_page_number)

            context['paginator'] = paginator
            context['page_obj'] = page_obj
        return context


def search_knowledge_by_name(request):
    """Поиск знаний по имени
    возвращает size результатов
    query=параметр поиска
    используется для подбора знаний
    """
    DEFAULT_SIZE = 100
    size = request.GET.get('size') or DEFAULT_SIZE
    query = request.GET.get('query') or ''

    result = (Znanie.objects
                .filter(tz__is_systemic=False, is_published=True, name__icontains=query)
                .values("id", "name")
                .order_by("name")[:int(size)])

    return JsonResponse(list(result), safe=False)
