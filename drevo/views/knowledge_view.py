from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView

from drevo.forms.knowledge_create_form import ZnanieCreateForm, ZnImageFormSet, ZnFilesFormSet
from drevo.models import Znanie


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

        # формирование списка Знаний по категориям
        zn = Znanie.published.all().prefetch_related('tz', 'author')

        context['zn_queryset'] = zn
        return context


class KnowledgeCreateView(LoginRequiredMixin, CreateView):
    """
    Представление создания предзнания и знания
    Есть возможность создания модальной формы - она при сохранении вернет JSON
    и создается по другому шаблону
    """
    model = Znanie
    form_class = ZnanieCreateForm
    template_name = 'drevo/tmpl_knowledge/knowledge_create.html'
    template_name_modal = 'drevo/tmpl_knowledge/knowledge_create_modal.html'
    error_message = 'Произошла ошибка при создании Знания'

    def get_context_data(self, **kwargs):
        """Передает контекст в шаблон"""
        context = super().get_context_data(**kwargs)
        # Формируем наименование страницы в зависимости от того является пользователь экспертом или нет
        if self.request.user.is_expert:
            context['title'] = 'Создание Знания/ПредЗнания'
        else:
            context['title'] = 'Создание ПредЗнания'

        # Передаем формы для создания знания и добавления фотографий к знанию
        if self.request.POST:
            context['image_form'] = ZnImageFormSet(self.request.POST, self.request.FILES)
            context['files_form'] = ZnFilesFormSet(self.request.POST, self.request.FILES)
        else:
            context['image_form'] = ZnImageFormSet()
            context['files_form'] = ZnFilesFormSet()

        # модальная форма - если в URL есть параметр modal или в POST
        is_modal = ('modal' in self.request.GET) or ('modal' in self.request.POST)
        context['modal_form'] = is_modal

        # для модальной формы меняем шаблон
        if is_modal:
            self.template_name = self.template_name_modal

        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.is_published = True
        response = super(KnowledgeCreateView, self).form_valid(form)
        context = self.get_context_data()
        image_form = context['image_form']
        files_form = context['files_form']
        if image_form.is_valid():
            image_form.instance = self.object
            image_form.save()

        if files_form.is_valid():
            files_form.instance = self.object
            files_form.save()

        if not context['modal_form']:
            return response
        else:
            # в модальной форме ответом будет json
            return JsonResponse(data={'id': self.object.pk, 'name': self.object.name},
                                status=201,  # created
                                json_dumps_params={'ensure_ascii': False})

    def form_invalid(self, form):
        form.add_error(None, self.error_message)
        return super().form_invalid(form)

    def get_success_url(self):
        # если задан параметр next, то переходим по нему
        if 'next' in self.request.GET:
            return redirect(self.request.GET['next'])
        else:
            return reverse_lazy('zdetail', kwargs={'pk': self.object.pk})


