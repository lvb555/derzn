import urllib
from ..models import *
from django.db.models import (Q,
                              QuerySet)
from itertools import permutations, combinations


class SearchEngineMixin:
    pass
    # def get_parameters_string(self, include_params: list[str] = None, exclude_params: list[str] = None):
    #     if include_params and include_params:
    #         raise Exception('Указаны и включаемые и исключаемые параметры')
    #
    #     parameters = dict()
    #     if include_params:
    #         for parameter, value in self.request.GET.items():
    #             if parameter in include_params:
    #                 parameters[parameter] = value
    #     elif exclude_params:
    #         for parameter, value in self.request.GET.items():
    #             if parameter not in exclude_params:
    #                 parameters[parameter] = value
    #
    #     return urllib.parse.urlencode(parameters)
    #
    # def get_query(self,
    #               fields_name: list[str],
    #               parameter_value: str,
    #               lookup: str = '',
    #               connector='AND'):
    #
    #     if not isinstance(fields_name, list):
    #         fields_name = [fields_name]
    #
    #     result_query = Q()
    #     # Так как sqlite не может искать без учета регистра,
    #     # будем искать и с заглавной буквы и с маленькой
    #     for field_name in fields_name:
    #         query = Q(**{field_name + lookup: parameter_value})
    #
    #         if not parameter_value.istitle():
    #             query = query.__or__(Q(
    #                 **{field_name + lookup: parameter_value.capitalize()}))
    #
    #         query_upper = Q(
    #             **{field_name + lookup: parameter_value.upper()})
    #
    #         query_lower = Q(
    #             **{field_name + lookup: parameter_value.lower()})
    #
    #         query = (query.__or__(query_upper)
    #                  .__or__(query_lower))
    #
    #         if connector == 'AND':
    #             result_query = result_query.__and__(query)
    #         elif connector == 'OR':
    #             result_query = result_query.__or__(query)
    #         else:
    #             raise Exception(f'Некорректный коннектор {connector}')
    #     return result_query
    #
    # def get_parameter_combinations(self, main_search_parameter: str):
    #     parameters = main_search_parameter.split()
    #     parameters = [self.cut_ending_word(par) for par in parameters]
    #     parameter_combinations = []
    #     for num_elements in range(len(parameters), 0, -1):
    #         for combination in combinations(parameters, num_elements):
    #
    #             parameter_combinations.append(combination)
    #     return parameter_combinations
    #
    # def cut_ending_word(self, value):
    #     vowels = ['а', 'е', 'ё', 'и', 'й', 'о', 'у', 'ы', 'э', 'ю' 'я']
    #     vowels = vowels + [char.capitalize() for char in vowels]
    #     if vowels[-1] not in vowels:
    #         return value
    #
    #     if len(value) <= 3:
    #         return value
    #
    #     result = []
    #
    #     cut_off_the_end = False
    #     for char in reversed(value):
    #         if cut_off_the_end or char not in vowels:
    #             cut_off_the_end = True
    #             result.append(char)
    #     value = ''.join(reversed(result))
    #     return value
