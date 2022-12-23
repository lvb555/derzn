from django.views.generic import TemplateView
from ..models import Category, Znanie
from ..models import Category, Znanie
from loguru import logger


logger.add('logs/main.log',
           format="{time} {level} {message}", rotation='100Kb', level="ERROR")


class KnowledgeView(TemplateView):
    """
    Выводит древо с иерархией категорий
    """
    template_name = 'drevo/knowledge.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        """
        Передает данные в шаблон
        """
        context = super().get_context_data(**kwargs)
        # формирует список категорий
        categories = Category.tree_objects.exclude(is_published=False)
        context['ztypes'] = categories

        # формирование списка Знаний по категориям
        zn = Znanie.published.all()
        zn_dict = {}
        for category in categories:
            zn_in_this_category = zn.filter(
                category=category).order_by('-order')
            zn_dict[category.name] = zn_in_this_category
        context['zn_dict'] = zn_dict

        return context