from django.db.models import Count, Q
from django.views.generic import ListView
from ..models import Author, AuthorType
from ..models import Author, AuthorType
from ..forms import AuthorsFilterForm
from loguru import logger

logger.add('logs/main.log',
           format="{time} {level} {message}", rotation='100Kb', level="ERROR")


class AuthorsListView(ListView):
    """
    выводит список авторов
    """
    template_name = 'drevo/authors_list.html'
    model = Author
    context_object_name = 'authors'

    def get_queryset(self):
        """
        Возвращает queryset авторов в соответствии с фильтром, полученным из формы
        на странице со списком авторов
        """

        # получаем значение фильтра из запроса
        author_type_to_filter = self.request.GET.get('author_type')

        queryset = Author.objects.annotate(zn_num=Count(
            'znanie', filter=Q(znanie__is_published=True))).all().order_by('name')

        # валидируем значение и возвращаем queryset
        list_of_author_types = AuthorType.objects.all().values_list('id', flat=True)
        if author_type_to_filter not in list(map(str, list_of_author_types)):
            return queryset
        else:
            return queryset.filter(atype=author_type_to_filter)

    def get_context_data(self, *, object_list=None, **kwargs):
        """
        Контекст, передаваемый в шаблон
        """
        context = super().get_context_data(**kwargs)

        rform = AuthorsFilterForm(self.request.GET)
        rform.is_valid()
        context['rform'] = rform

        return context
