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


def get_knowledge_dict(knowledge, rights='expert', user=None):
    """
    Возвращает кортеж, который содержит кверисет с категориями и
    словарь, в котором ключи - категории, а значения - знания
    :param knowledge: кверисет со знаниями
    :param user: пользователь'
    :param rights: права пользователя (эксперт/руководитель)
    :return: кортеж: (категории, {категория: знания})
    """
    _knowledge_dict = {}
    # формирует список категорий
    _categories = Category.tree_objects.exclude(is_published=False)

    for category in _categories:
        if user:
            if rights == 'expert':
                experts = category.get_expert_ancestors_category()
            else:
                experts = category.get_admin_ancestors_category()

            if user in experts:
                zn_in_this_category = knowledge.filter(
                    category=category)
                # Проверка, существуют ли в данной категории знания. Категория добавляется только в том
                # случае, если существует хотя бы одно знание
                if zn_in_this_category:
                    _knowledge_dict[category.name] = zn_in_this_category
        else:
            zn_in_this_category = knowledge.filter(
                category=category)
            if not zn_in_this_category:
                continue
            _knowledge_dict[category.name] = zn_in_this_category
    result_categories = []
    for category in _categories:
        if category.name in _knowledge_dict.keys():
            result_categories.append(category)
    return result_categories, _knowledge_dict


def set_auto_status(instance: Znanie, user, level):
    """
    Устанавливает автоматически статус в соответствии с таблицей переходов
    :param instance: Объект сущности Знание
    :param user: объект пользователя
    :param level: уровень технологического процесса
    """
    current_status = instance.get_current_status
    if level == 'expert' and current_status.status == 'PRE_FIN':
        new_status = 'PRE_EXP'
        instance.expert = user
    elif level == 'redactor':
        if current_status.status == 'FIN':
            new_status = 'REDACT'
        elif current_status.status == 'PRE_FIN_EXP':
            new_status = 'PRE_REDACT'
        else:
            return False
        instance.redactor = user
    elif level == 'director':
        instance.director = user
        instance.save()
        return False
    else:
        return False

    current_status.is_active = False
    current_status.save()
    KnowledgeStatuses.objects.create(
        knowledge=instance,
        status=new_status,
        user=user,
        is_active=True
    )
    instance.save()


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
            context['title'] = 'Создание Знания/ПредЗнания'
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
            knowledge = KnowledgeStatuses.objects.create(
                knowledge=knowledge,
                status=status,
                user=self.request.user
            )
            return HttpResponseRedirect(reverse('znanie_update', kwargs={'pk': knowledge.pk}))
        return self.form_invalid(form, image_form)

    def form_invalid(self, form, image_form):
        return self.render_to_response(self.get_context_data(form=form, image_form=image_form))


class UserKnowledgeProcessView(LoginRequiredMixin, TemplateView):
    """
    Представление этапа изменения знаний пользователя
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
        zn = Znanie.objects.filter((Q(user=user) &
                                    (Q(knowledge_status__status='WORK_PRE') |
                                     Q(knowledge_status__status='RET_PRE_EDIT') |
                                     Q(knowledge_status__status='PRE_FIN') |
                                     Q(knowledge_status__status='WORK') |
                                     Q(knowledge_status__status='RET_TO_EDIT') |
                                     Q(knowledge_status__status='FIN')
                                     ) & Q(knowledge_status__is_active=True))
                                   )

        context['ztypes'], context['zn_dict'] = get_knowledge_dict(zn)
        context['var'] = variables
        if self.request.user.is_expert:
            context['title'] = 'Изменение Знания/ПредЗнания'
        else:
            context['title'] = 'Изменение ПредЗнания'

        return context


class ExpertKnowledgeProcess(LoginRequiredMixin, TemplateView):
    """Представление страницы работы эксперта"""
    template_name = 'drevo/user_knowledge_process.html'

    def get_context_data(self, **kwargs):
        """
        Передает контекст в шаблон
        """
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Формирование списка неопубликованных знаний
        zn = Znanie.objects.filter(
            Q(is_published=False) &
            (
                    (Q(knowledge_status__status='PRE_FIN') |
                     Q(knowledge_status__status='PRE_REJ') |
                     (
                             (Q(knowledge_status__status='PRE_EXP') |
                              Q(knowledge_status__status='PRE_REF_EXP') |
                              Q(knowledge_status__status='PRE_FIN_EXP')
                              ) & Q(expert=user)
                     )
                     ) & Q(knowledge_status__is_active=True))
        )

        context['ztypes'], context['zn_dict'] = get_knowledge_dict(zn, user=user)
        context['var'] = variables
        context['title'] = 'Экспертиза ПредЗнания'

        return context


class RedactorKnowledgeProcess(LoginRequiredMixin, TemplateView):
    """Представление страницы работы редактора"""
    template_name = 'drevo/user_knowledge_process.html'

    def get_context_data(self, **kwargs):
        """
        Передает контекст в шаблон
        """
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Формирование списка неопубликованных знаний
        zn = Znanie.objects.filter(
            Q(is_published=False) &
            (
                    (Q(knowledge_status__status='PRE_FIN_EXP') |
                     Q(knowledge_status__status='FIN') |
                     (
                             (Q(knowledge_status__status='PRE_REDACT') |
                              Q(knowledge_status__status='PRE_REF_RED') |
                              Q(knowledge_status__status='PRE_FIN_RED') |
                              Q(knowledge_status__status='REDACT') |
                              Q(knowledge_status__status='REF_RED') |
                              Q(knowledge_status__status='FIN_RED')
                              ) & Q(redactor=user)
                     )
                     ) & Q(knowledge_status__is_active=True))
        ).exclude(user=user)

        context['ztypes'], context['zn_dict'] = get_knowledge_dict(zn)
        context['var'] = variables
        context['title'] = 'Редактирование ПредЗнания и Знания'

        return context


class DirectorKnowledgeProcess(LoginRequiredMixin, TemplateView):
    """Представление страницы работы редактора"""
    template_name = 'drevo/user_knowledge_process.html'

    def get_context_data(self, **kwargs):
        """
        Передает контекст в шаблон
        """
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Формирование списка неопубликованных знаний
        zn = Znanie.objects.filter(
            (Q(knowledge_status__status='PRE_FIN_RED') |
             Q(knowledge_status__status='FIN_RED') |
             Q(knowledge_status__status='PRE_REJ') |
             Q(knowledge_status__status='REJ') |
             (
                     (Q(knowledge_status__status='PUB_PRE') |
                      Q(knowledge_status__status='PRE_KLZ') |
                      Q(knowledge_status__status='PRE_EXP_2') |
                      Q(knowledge_status__status='PUB') |
                      Q(knowledge_status__status='KLZ') |
                      Q(knowledge_status__status='EXP_2')
                      ) & Q(director=user)
             )
             ) & Q(knowledge_status__is_active=True)
        ).exclude(user=user)

        context['ztypes'], context['zn_dict'] = get_knowledge_dict(zn)
        context['var'] = variables
        context['title'] = 'Публикация ПредЗнания и Знания'

        return context


class KlzKnowledgeProcess(LoginRequiredMixin, TemplateView):
    """Представление страницы работы члена КЛЗ"""
    template_name = 'drevo/user_knowledge_process.html'

    def get_context_data(self, **kwargs):
        """
        Передает контекст в шаблон
        """
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Формирование списка неопубликованных знаний
        zn = Znanie.objects.filter(
            Q(is_published=False) &
            ((Q(knowledge_status__status='PRE_KLZ') |
              Q(knowledge_status__status='KLZ')) & Q(knowledge_status__is_active=True)))

        context['ztypes'], context['zn_dict'] = get_knowledge_dict(zn)
        context['var'] = variables
        context['title'] = 'Клуб любителей знания (КЛЗ)'

        return context


class KnowledgeUpdateView(LoginRequiredMixin, UpdateView):
    """Класс представления изменения знания"""
    model = Znanie
    form_class = ZnanieUpdateForm
    template_name = 'drevo/knowledge_update.html'
    success_url = reverse_lazy('drevo')

    def get_context_data(self, **kwargs):
        """Передает контекст в шаблон"""
        context = super().get_context_data(**kwargs)
        tp_level = self.request.GET.get('level')
        # Формируем наименование страницы в зависимости от того является пользователь экспертом или нет
        if tp_level == 'expert':
            context['title'] = 'Экспертиза ПредЗнания'
        elif self.request.user.is_expert:
            context['title'] = 'Изменение Знания/Предзнания'
        else:
            context['title'] = 'Изменение ПредЗнания'

        knowledge_pk = self.kwargs.get('pk')
        knowledge = Znanie.objects.get(pk=knowledge_pk)

        if knowledge:
            # Получаем возможные действия
            current_status = knowledge.get_current_status.status
            if tp_level == 'expert':
                actions = variables.TRANSITIONS_EXP[current_status]
            elif tp_level == 'redactor':
                actions = variables.TRANSITIONS_RED[current_status]
            elif tp_level == 'director':
                actions = variables.TRANSITIONS_DIRECT[current_status]
            else:
                actions = variables.TRANSITIONS_PUB[current_status]
            context['actions'] = actions

        context['pk'] = knowledge_pk

        return context

    def get(self, request, *args, **kwargs):
        """Обрабатывает GET запрос"""
        self.object = self.get_object()

        # Выполняем автоматическое изменение статуса при открытии в соответствии с таблицей переходов
        tp_level = self.request.GET.get('level')
        if tp_level:
            set_auto_status(self.object, self.request.user, tp_level)

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
            return HttpResponseRedirect(reverse('znanie_update', kwargs={'pk': knowledge.pk}))
        return self.form_invalid(form, image_form)

    def form_invalid(self, form, image_form):
        return self.render_to_response(self.get_context_data(form=form, image_form=image_form))


class KnowledgeChangeStatus(LoginRequiredMixin, UpdateView):
    """Изменяет статус знания"""
    success_url = reverse_lazy('drevo')

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
        if status == 'PUB_PRE' or status == 'PUB':
            knowledge.is_published = True
            knowledge.save()
        if status == 'PRE_KLZ' or status == 'KLZ':
            knowledge.is_published = False
            knowledge.save()
        return HttpResponseRedirect(reverse('drevo'))
