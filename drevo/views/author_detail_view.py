

from django.views.generic import DetailView

from loguru import logger

from ..models import Author, Znanie
from ..relations_tree import get_knowledges_by_categories


logger.add('logs/main.log',
           format="{time} {level} {message}", rotation='100Kb', level="ERROR")


class AuthorDetailView(DetailView):
    """
    Выводит подробную информацию об Авторе
    """
    model = Author
    context_object_name = 'author'
    template_name = 'drevo/author_details.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        """
        Контекст, передаваемый в шаблон
        """
        context = super().get_context_data(**kwargs)

        # получаем знания данного автора
        knowledges_of_author = Znanie.published.filter(
            author__id=int(self.kwargs['pk']))

        context['categories'], context['knowledges'] = \
            get_knowledges_by_categories(knowledges_of_author)

        return context
