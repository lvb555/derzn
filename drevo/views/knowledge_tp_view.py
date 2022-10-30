from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, TemplateView, UpdateView

from drevo.common import variables
from drevo.forms.knowledge_create_form import ZnanieCreateForm, ZnImageFormSet
from drevo.forms.knowledge_update_form import ZnanieUpdateForm, ZnImageEditFormSet
from drevo.models import Znanie, KnowledgeStatuses, Category


def get_knowledge_dict(knowledge):
    """
    Возвращает кортеж, который содержит кверисет с категориями и
    словарь, в котором ключи - категории, а значения - знания
    :param knowledge: кверисет со знаниями
    :return: кортеж: (категории, {категория: знания})
    """
    _knowledge_dict = {}
    # формирует список категорий
    _categories = Category.tree_objects.exclude(is_published=False)

    for category in _categories:
        zn_in_this_category = knowledge.filter(
            category=category)
        _knowledge_dict[category.name] = zn_in_this_category

    return _categories, _knowledge_dict


class KnowledgeCreateView(LoginRequiredMixin, CreateView):
    """
    Представление создания предзнания и знания
    """
    model = Znanie
    form_class = ZnanieCreateForm
    template_name = 'drevo/knowledge_create.html'
    success_url = reverse_lazy('znanie_user_process')

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
            return HttpResponseRedirect(reverse('znanie_user_process'))
        return self.form_invalid(form, image_form)

    def form_invalid(self, form, image_form):
        return self.render_to_response(self.get_context_data(form=form, image_form=image_form))


class UserKnowledgeProcessView(LoginRequiredMixin, TemplateView):
    """
    Представление этапа редактирования знаний пользователя
    """
    template_name = 'drevo/user_knowledge_process.html'

    def get_context_data(self, **kwargs):
        """
        Передает контекст в шаблон
        """
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # формирование списка Знаний по категориям
        # Формирование списка опубликованных знаний и знаний, созданных пользователем
        zn = Znanie.objects.filter(Q(is_published=True) | Q(user=user))

        context['ztypes'], context['zn_dict'] = get_knowledge_dict(zn)
        context['var'] = variables
        if self.request.user.is_expert:
            context['title'] = 'Изменение Знания'
        else:
            context['title'] = 'Изменение ПредЗнания'

        return context


class KnowledgeUpdateView(LoginRequiredMixin, UpdateView):
    """Класс представления редактирования знания"""
    model = Znanie
    form_class = ZnanieUpdateForm
    template_name = 'drevo/knowledge_update.html'
    success_url = reverse_lazy('znanie_user_process')

    def get_context_data(self, **kwargs):
        """Передает контекст в шаблон"""
        context = super().get_context_data(**kwargs)
        # Формируем наименование страницы в зависимости от того является пользователь экспертом или нет
        if self.request.user.is_expert:
            context['title'] = 'Редактирование Знания'
        else:
            context['title'] = 'Редактирование ПредЗнания'

        knowledge_pk = self.kwargs.get('pk')
        knowledge = Znanie.objects.get(pk=knowledge_pk)
        # Так как любой пользователь может создавать предзнания, получаем возможные действия как для публики
        if knowledge:
            current_status = knowledge.get_current_status.status
            actions = variables.TRANSITIONS_PUB[current_status]
            context['actions'] = actions

        context['pk'] = knowledge_pk

        return context

    def get(self, request, *args, **kwargs):
        """Обрабатывает GET запрос"""
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        image_form = ZnImageEditFormSet(instance=self.object)
        return self.render_to_response(self.get_context_data(form=form, image_form=image_form))

    def post(self, request, *args, **kwargs):
        """Обрабатывает POST запрос"""
        self.object = self.get_object()
        # Получаем форму для заполнения данных Знания
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        # Получаем форму для прикрепления фотографий
        image_form = ZnImageEditFormSet(self.request.POST, self.request.FILES, instance=self.object)
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
            return HttpResponseRedirect(reverse('znanie_user_process'))
        return self.form_invalid(form, image_form)

    def form_invalid(self, form, image_form):
        return self.render_to_response(self.get_context_data(form=form, image_form=image_form))


class KnowledgeChangeStatus(LoginRequiredMixin, UpdateView):
    """Изменяет статус знания"""
    success_url = reverse_lazy('znanie_user_process')

    def get(self, request, *args, **kwargs):
        knowledge_pk = self.kwargs.get('pk')
        status = self.kwargs.get('status')
        knowledge = get_object_or_404(Znanie, pk=knowledge_pk)
        old_status = knowledge.get_current_status
        old_status.is_active = False
        old_status.save()
        new_status = KnowledgeStatuses.objects.create(
            knowledge=knowledge,
            status=status,
            user=request.user,
            is_active=True
        )
        return HttpResponseRedirect(reverse('znanie_user_process'))
