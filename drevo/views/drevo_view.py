from django.db.models import Q
from django.views.generic import TemplateView

from ..models import Category, Znanie
from loguru import logger

logger.add('logs/main.log',
           format="{time} {level} {message}", rotation='100Kb', level="ERROR")


class DrevoView(TemplateView):
    """
    Выводит древо с иерархией категорий
    """
    template_name = 'drevo/drevo.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        """
        Передает данные в шаблон
        """
        context = super().get_context_data(**kwargs)
        # формирует список категорий
        categories = Category.tree_objects.exclude(is_published=False)
        context['ztypes'] = categories

        # формирование списка Знаний по категориям
        # Формирование списка опубликованных знаний
        zn = Znanie.published.all()
        # Формирование списка знаний для пользователей-членов КЛЗ
        if self.request.user.is_authenticated and self.request.user.in_klz:
            zn = Znanie.objects.filter(Q(is_published=False) &
                                       ((Q(knowledge_status__status='PRE_KLZ') |
                                         Q(knowledge_status__status='KLZ')) & Q(knowledge_status__is_active=True)))
        zn_dict = {}
        for category in categories:
            zn_in_this_category = zn.filter(
                category=category).order_by('-order')
            zn_dict[category.name] = zn_in_this_category
        context['zn_dict'] = zn_dict

        return context
