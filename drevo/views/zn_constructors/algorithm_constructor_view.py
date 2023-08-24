from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from drevo.models import Znanie
from drevo.relations_tree import get_descendants_for_knowledge


class AlgorithmConstructorView(LoginRequiredMixin, TemplateView):
    """
    Отображение страницы "Конструктор алгоритмов"
    """
    template_name = 'drevo/algorithm_constructor/algorithm_constructor.html'

    def get_context_data(self, **kwargs):
        """Передает контекст в шаблон"""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Конструктор алгоритмов'
        pk = self.kwargs.get('pk')
        if pk == '0':
            context["new_algorithm"] = True
            return context

        selected_algorithm = Znanie.objects.get(id=pk)
        context['title'] = 'Конструктор алгоритмов'
        context['znanie'] = selected_algorithm
        context['relative_znaniya'] = get_descendants_for_knowledge(selected_algorithm)

        return context


def algorithm_checking():
    names_of_errors = {
        'required_relation': 'Нет обязательной связи',
        'condition': 'У знания вида <Условие> отсутствует связь <Тогда>/<Если>',
        'not_only_rel': 'Связь не является единственной',

    }

