from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, TemplateView

from drevo.forms.knowledge_create_form import ZnanieCreateForm, ZnImageFormSet
from drevo.models import Znanie, KnowledgeStatuses, Category


class KnowledgeCreateView(LoginRequiredMixin, CreateView):
    """
    Представление создания предзнания и знания
    """
    model = Znanie
    form_class = ZnanieCreateForm
    template_name = 'drevo/knowledge_create.html'
    success_url = reverse_lazy('znanie_process')

    def get_context_data(self, **kwargs):
        """Передает контекст в шаблон"""
        context = super().get_context_data(**kwargs)
        # Формируем наименование страницы в зависимости от того является пользователь экспертом или нет
        if self.request.user.is_expert:
            context['title'] = 'Создание Знания'
        else:
            context['title'] = 'Создание ПредЗнания'

        # Передаем формы для создания знания и добавления фотографий к знанию
        if self.request.POST:
            context['form'] = ZnanieCreateForm(self.request.POST)
            context['image_form'] = ZnImageFormSet(self.request.POST)
        else:
            context['form'] = ZnanieCreateForm()
            context['image_form'] = ZnImageFormSet()
        return context

    def get(self, request, *args, **kwargs):
        """Обрабатывает GET запрос"""
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        image_form = ZnImageFormSet()
        return self.render_to_response(self.get_context_data(form=form, image_form=image_form))

    def post(self, request, *args, **kwargs):
        """Обрабатывает POST запрос"""
        self.object = None
        # Получаем форму для заполнения данных Знания
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        # Получаем форму для прикрепления фотографий
        image_form = ZnImageFormSet(self.request.POST, self.request.FILES)
        if form.is_valid() and image_form.is_valid():
            # Перед сохранением формы в поле user подставляем текущего пользователя
            knowledge = form.save(commit=False)
            knowledge.user = request.user
            # Сохраняем Знание
            knowledge.save()
            form.save_m2m()
            # Перед сохранением формы с изображениями подставляем текущий объект знания
            image_form.instance = knowledge
            image_form.save()
            # Создаем запись со статусом для текущего знания
            if self.request.user.is_expert and self.request.user in knowledge.get_expert():
                status = 'WORK'
            else:
                status = 'WORK_PRE'
            KnowledgeStatuses.objects.create(
                knowledge=knowledge,
                status=status,
                user=self.request.user
            )
            return HttpResponseRedirect(reverse('znanie_process'))
        return self.form_invalid(form, image_form)

    def form_invalid(self, form, image_form):
        return self.render_to_response(self.get_context_data(form=form, image_form=image_form))


class KnowledgeProcessView(LoginRequiredMixin, TemplateView):
    """
    Представление этапов работы со знанием/предзнанием
    """
    template_name = 'drevo/knowledge_process.html'

    def get_context_data(self, **kwargs):
        """
        Передает контекст в шаблон
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
            zn = Znanie.objects.filter(Q(is_published=True) | Q(knowledge_status__status='KLZ'))
        zn_dict = {}
        for category in categories:
            zn_in_this_category = zn.filter(
                category=category).order_by('-order')
            zn_dict[category.name] = zn_in_this_category
        context['zn_dict'] = zn_dict

        return context
