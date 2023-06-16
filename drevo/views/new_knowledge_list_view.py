import datetime
from django.views.generic import ListView
from drevo.models import Znanie, Category
from .popular_knowledges import get_unmarked_children
from ..forms import DatePickNewForm
from loguru import logger


logger.add('logs/main.log',
           format="{time} {level} {message}", rotation='100Kb', level="ERROR")


class NewKnowledgeListView(ListView):
    """
    полный список недавно опубликованных знаний
    """
    model = Znanie
    template_name = 'drevo/new_knowledge_date_table.html'
    context_object_name = 'categorized_new_knowledges'


    def get_queryset(self):
        """Возвращает отфильтрованный QuerySet"""
        date_form = DatePickNewForm(self.request.GET)
        date_for_new = datetime.date.today() - datetime.timedelta(days=7)
        selected_category = self.request.GET.get('knowledge_category')
        if date_form.is_valid():
            date_for_new = date_form.cleaned_data.get('date')
        filtered_knowledges = Znanie.objects.filter(date__gte=date_for_new,
                                            is_published=True, tz__is_systemic=False)
        if selected_category != '-1' and selected_category is not None:
                category_and_descendants = Category.objects.get(pk=selected_category).get_descendants(
                    include_self=True).filter(is_published=True)
                filtered_knowledges = filtered_knowledges.filter(category__in=category_and_descendants)
                filtered_knowledges = get_unmarked_children(filtered_knowledges)
        return filtered_knowledges

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        _get = self.request.GET.dict()
        form_to_validate = DatePickNewForm(_get)
        if _get and form_to_validate.is_valid():
            context['datepick_form'] = DatePickNewForm(_get)
            selected_category = _get.get('knowledge_category')
            context['selected_category'] = int(selected_category)
        else:
            context['datepick_form'] = DatePickNewForm()
        context['categories'] = Category.tree_objects.filter(is_published=True)
        return context
