from django.views.generic import DetailView
from ..models import Znanie
from ..models import Znanie, Label
from loguru import logger
from ..relations_tree import get_knowledges_by_categories


logger.add('logs/main.log',
           format="{time} {level} {message}", rotation='100Kb', level="ERROR")


class ZnanieByLabelView(DetailView):
    """
    выводит сущности Знание для заданной метки
    """
    template_name = 'drevo/zlabel.html'
    model = Label
    context_object_name = 'label'

    def get_context_data(self, *, object_list=None, **kwargs):
        """
        Контекст, передаваемый в шаблон
        """
        context = super().get_context_data(**kwargs)

        # получаем знания, содержащие данную метку

        label_id = int(self.kwargs['pk'])
        label = Label.objects.get(id=label_id)
        knowledges_of_label = Znanie.published.filter(labels__in=[label])

        context['knowledge_by'] = self.request.GET.get('knowledge_by')
        if context['knowledge_by']:
            context['categories'], context['knowledges'] = \
                get_knowledges_by_categories(knowledges_of_label)
        else:
            context['knowledges_of_label'] = knowledges_of_label

        for z in knowledges_of_label:
            logger.debug(z.labels)

        return context
