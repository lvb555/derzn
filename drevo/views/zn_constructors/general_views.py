from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.views.generic import CreateView, TemplateView

from drevo.forms.knowledge_create_form import ZnImageFormSet, ZnFilesFormSet
from drevo.forms.constructor_knowledge_form import MainZnInConstructorCreateEditForm
from drevo.models import Znanie, SpecialPermissions, Tz, Suggestion

from .supplementary_functions import create_zn_for_constructor, get_images_from_request, \
    get_file_from_request
from .mixins import DispatchMixin
from ...relations_tree import get_descendants_for_knowledge


class ZnaniyaForConstructorView(LoginRequiredMixin, DispatchMixin, TemplateView):
    """
    Представление страницы, в которой знания в компетенциях эксперта/руководителя строятся в виде дерева
    для последующего открытия конструктора
    """
    template_name = 'drevo/constructors/constructor_start_page.html'

    def __init__(self):
        super().__init__()
        self.type_of_zn = None

    @staticmethod
    def get_queryset(user, tz_name: str):
        """Метод для получения опубликованных сложных знаний конкретного вида в компетенции эксперта"""
        tz_name_mapping = {
            'algorithm': 'Алгоритм',
            'document': 'Документ',
            'filling_tables': 'Таблица',
            'table': 'Таблица',
            'quiz': 'Тест',
        }

        user_competencies = SpecialPermissions.objects.filter(expert=user).first()
        user_competencies = (
            user_competencies.categories.all() if not tz_name == 'table' else user_competencies.admin_competencies.all()
        )

        tz_type = Tz.t_(tz_name_mapping.get(tz_name))
        queryset = Znanie.published.select_related('category').filter(tz=tz_type, category__in=user_competencies).distinct()

        return queryset

    def get_context_data(self, **kwargs):
        """Передает контекст в шаблон"""
        context = super().get_context_data(**kwargs)
        user = self.request.user
        self.type_of_zn = self.request.GET.get('type_of_zn')
        context['knowledge'] = self.get_queryset(user=user, tz_name=self.type_of_zn)

        title_mapping = {
            'filling_tables': 'Наполнение таблиц',
            'table': 'Конструктор таблиц',
            'quiz': 'Конструктор тестов',
            'algorithm': 'Конструктор алгоритмов',
            'document': 'Конструктор документов'
        }
        context['title'] = title_mapping.get(self.type_of_zn)
        context['type_of_page'] = self.type_of_zn

        return context


class MainZnInConstructorCreateView(LoginRequiredMixin, DispatchMixin, CreateView):
    """Представление создания главного знания для конструктора знания (виды Тест, Таблица, Алгоритм)"""
    model = Znanie
    form_class = MainZnInConstructorCreateEditForm
    template_name = 'drevo/constructors/main_zn_create.html'

    def __init__(self):
        super().__init__()
        self.object = None
        self.type_of_zn = None

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['type_of_zn'] = self.type_of_zn
        return kwargs

    def get_context_data(self, **kwargs):
        """Передает контекст в шаблон"""
        context = super().get_context_data(**kwargs)
        context['action'] = 'create'
        title_mapping = {
            'algorithm': 'Создание алгоритма',
            'document': 'Создание документа',
            'table': 'Создание таблицы',
            'quiz': 'Создание теста',
        }
        self.type_of_zn = self.kwargs.get('type_of_zn')
        context['type_of_zn'] = self.type_of_zn
        context['title'] = title_mapping.get(self.type_of_zn)

        # Передаем формы для создания знания и добавления фотографий к знанию
        if self.request.POST:
            context['zn_form'] = MainZnInConstructorCreateEditForm(self.request.POST, type_of_zn=self.type_of_zn)
            context['image_form'] = ZnImageFormSet(self.request.POST)
        else:
            context['zn_form'] = MainZnInConstructorCreateEditForm(user=self.request.user, type_of_zn=self.type_of_zn)
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
        self.type_of_zn = self.kwargs.get('type_of_zn')
        # Получаем форму для заполнения данных Знания
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        # Получаем форму для прикрепления фотографий
        image_form = ZnImageFormSet(self.request.POST, self.request.FILES)
        if form.is_valid() and image_form.is_valid():
            # Перед сохранением формы в поле user подставляем значения по умолчанию
            knowledge = form.save(commit=False)
            create_zn_for_constructor(knowledge, form, request, author=True, image_form=image_form)
            self.object = knowledge

            if self.type_of_zn == 'algorithm' or self.type_of_zn == 'document':
                return HttpResponseRedirect(reverse('tree_constructor', kwargs={'type': self.type_of_zn, 'pk': knowledge.pk}))
            elif self.type_of_zn == 'quiz':
                return HttpResponseRedirect(reverse('quiz_constructor', kwargs={'pk': knowledge.pk}))
            elif self.type_of_zn == 'table':
                # указываем на возврат по кнопке «Закрыть» на нашу страницу
                params = '?prev=' + reverse('znaniya_for_constructor')+'?type_of_zn=table'
                return HttpResponseRedirect(reverse('table_constructor', kwargs={'pk': knowledge.pk})+params)

        return self.form_invalid(form, image_form)

    def form_invalid(self, form, image_form):
        return self.render_to_response(self.get_context_data(form=form, image_form=image_form))


@require_http_methods(['POST'])
def edit_main_zn_in_constructor(request):
    """Редактирование атрибутов знания, прикрепленных изображений и файла главного сложного знания в конструкторе"""
    req_data = request.POST
    existing_knowledge = get_object_or_404(Znanie, id=req_data.get('main_zn_id'))
    form = MainZnInConstructorCreateEditForm(data=req_data, instance=existing_knowledge, user=request.user,
                                             type_of_zn='algorithm')
    images_form = ZnImageFormSet(req_data, get_images_from_request(request=request), instance=existing_knowledge)
    file_form = ZnFilesFormSet(req_data, get_file_from_request(request=request), instance=existing_knowledge)

    if form.is_valid() and images_form.is_valid() and file_form.is_valid():
        knowledge = form.save(commit=False)
        create_zn_for_constructor(knowledge, form, request, image_form=images_form, file_form=file_form)
        return JsonResponse(data={'zn_id': knowledge.id, 'zn_name': knowledge.name}, status=200)
    return JsonResponse(data={}, status=400)


def delete_complex_zn(request):
    """Удаление сложного знания: главного знания и всех связанных знаний"""
    main_zn = get_object_or_404(Znanie, id=request.GET.get('id'))
    rel_znaniya = get_descendants_for_knowledge(main_zn)
    for zn in rel_znaniya:
        zn.delete()
    main_zn.delete()
    return HttpResponse(status=200)



class UnprocessedSuggestionsTreeView(LoginRequiredMixin, TemplateView):
    template_name = 'drevo/constructors/constructor_start_page.html'

    def get_unprocessed_suggestions(self, user):
        user_competencies = SpecialPermissions.objects.filter(expert=user).first().admin_competencies.all()
        knowledge_with_unprocessed_suggestions_ids = Suggestion.objects.filter(
            parent_knowlege__category__in=user_competencies,
            is_approve=None).values_list('parent_knowlege', flat=True).distinct()

        knowledge_with_unprocessed_suggestions = Znanie.objects.filter(
            id__in=knowledge_with_unprocessed_suggestions_ids)

        return knowledge_with_unprocessed_suggestions

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        knowledge_with_unprocessed_suggestions = self.get_unprocessed_suggestions(user)

        context['knowledge'] = knowledge_with_unprocessed_suggestions
        context['type_of_page'] = 'suggestion'
        return context