from django.urls import reverse_lazy
from ..forms import *
from django.views.generic.edit import FormView
from ..models import *
from django.core.paginator import Paginator
from django.db.models import (Q,
                              QuerySet,
                              Count,
                              Value)
from .search_engine import SearchEngineMixin
from itertools import permutations


class TagSearchView(FormView, SearchEngineMixin):
    template_name = "drevo/search.html"
    form_class = TagSearchForm
    success_url = reverse_lazy("search_tag")

    def get_parameter_combinations(self, main_search_parameter: str):
        parameters = main_search_parameter.split()
        parameter_combinations = []
        for num_elements in range(len(parameters), 0, -1):
            for combination in permutations(parameters, num_elements):
                combination_to_string = ' '.join(combination)
                parameter_combinations.append(combination_to_string)
        return parameter_combinations

    def cut_ending_word(self, value):
        # breakpoint()
        vowels = ['а', 'е', 'ё', 'и', 'й', 'о', 'у', 'ы', 'э', 'ю' 'я']
        vowels = vowels + [char.capitalize() for char in vowels]
        if vowels[-1] not in vowels:
            return value

        if len(value) <= 3:
            return value

        result = []

        cut_off_the_end = False
        for char in reversed(value):
            if cut_off_the_end or char not in vowels:
                cut_off_the_end = True
                result.append(char)
        value = ''.join(reversed(result))
        return value

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

        result_tags = []
        if main_search_parameter:
            # Ищем знания по главному полю
            parameter_value_combinations = self.get_parameter_combinations(
                main_search_parameter)
            result_query = None
            for value in parameter_value_combinations:
                value = self.cut_ending_word(value)

                query = self.get_query(fields_name=['name'],
                                       parameter_value=value,
                                       lookup='__contains',
                                       )

                tags_tmp = tags.filter(query)

                if not result_tags:
                    result_tags = list(tags_tmp)
                else:
                    for tag in list(tags_tmp):
                        if tag not in result_tags:
                            result_tags.append(tag)

        return result_tags

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Поиск тегов'
        main_search_parameter = self.request.GET.get('main_search')

        # Для сохранения любого пользовательского ввода в форме
        context['form'] = TagSearchForm(self.request.GET)

        if main_search_parameter:

            # Для соединение с параметрами пагинации
            context['search_string_parameters'] = self.get_parameters_string(
                exclude_params=['page'])

            tags = self.get_published_tags_with_filter(
                main_search_parameter=main_search_parameter,
            )

            # tags = tags.select_related('atype')

            # tags = tags.order_by('name')

            paginator = Paginator(tags, 10)

            cur_page_number = self.request.GET.get('page')

            page_obj = paginator.get_page(cur_page_number)

            context['paginator'] = paginator
            context['page_obj'] = page_obj

        return context
