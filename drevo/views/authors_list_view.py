from django.db.models import Count
from django.views.generic import ListView
from ..models import Author, AuthorType
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
    paginate_by = 25

    def get_queryset(self):
        if search_data := self.request.GET.get('author_for_search'):
            return (
                Author.objects
                .filter(znanie__is_published=True, name__icontains=search_data)
                .annotate(zn_num=Count('znanie')).order_by('name')
            )
        return Author.objects.filter(znanie__is_published=True).annotate(zn_num=Count('znanie')).order_by('name')

    def get_context_data(self, *, object_list=None, **kwargs):
        """
        Контекст, передаваемый в шаблон
        """
        context = super().get_context_data(**kwargs)
        types = self.get_queryset().values_list('atype', flat=True).distinct()
        context['author_types'] = AuthorType.objects.filter(pk__in=types)
        if author_for_search := self.request.GET.get('author_for_search'):
            context['author_for_search'] = author_for_search
        return context
