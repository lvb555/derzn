from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, FormView
from django.db.models import Q

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from drevo.models import RelationshipTzTr, Znanie
from drevo.relations_tree import get_descendants_for_knowledge
from drevo.views.zn_constructors.mixins import DispatchMixin
from django.views.decorators.http import require_http_methods

from drevo.forms.constructor_knowledge_form import RelationForZnInAlgorithm, ZnForAlgorithmCreateUpdateForm
from .supplementary_functions import create_zn_for_constructor, create_relation


class AlgorithmConstructorView(LoginRequiredMixin, TemplateView):
    """
    Отображение страницы "Конструктор алгоритмов"
    """
    template_name = 'drevo/algorithm_constructor/algorithm_constructor.html'

    def get_context_data(self, **kwargs):
        """Передает контекст в шаблон"""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Конструктор алгоритмов'
        pk = self.kwargs.get('pk')
        if pk == '0':
            context["new_algorithm"] = True
            return context

        selected_algorithm = Znanie.objects.get(id=pk)
        context['title'] = 'Конструктор алгоритмов'
        context['znanie'] = selected_algorithm
        context['relative_znaniya'] = get_descendants_for_knowledge(selected_algorithm)

        return context


class RelationForAlgorithmCreateEditView(LoginRequiredMixin, TemplateView, DispatchMixin):
    """Представление создания знаний - строк и столбцов для таблицы"""
    model = Znanie
    form_class = ZnForAlgorithmCreateUpdateForm
    template_name = 'drevo/algorithm_constructor/zn_and_rel_for_algorithm_create.html'

    def __init__(self):
        super().__init__()
        self.parent_id = None
        self.parent_zn_tz = None

    # def get(self, *args, **kwargs):
    #     """Обрабатывает GET запрос"""
    #     self.object = None
    #     self.parent_id = self.kwargs.get('parent_id')
    #     self.parent_zn_tz = get_object_or_404(Znanie, id=self.parent_id).tz
    #     form_class = self.get_form_class()
    #     zn_create_form = self.get_form(form_class)
    #     rel_attr_form = RelationForZnInAlgorithm(parent_zn_tz=self.parent_zn_tz)
    #     return self.render_to_response(self.get_context_data(zn_create_form=zn_create_form, rel_attr_form=rel_attr_form))

    def get_context_data(self, **kwargs):
        """Передает контекст в шаблон"""
        context = super().get_context_data(**kwargs)
        parent_id = self.request.GET.get('parent_id')
        action = self.kwargs.get('action')
        context['title'] = 'Создание связи'
        context['action'] = 'create'

        context['base_kn'] = {parent_id: get_object_or_404(Znanie, id=parent_id)}
        print(context['base_kn'])

        # Передаем формы для создания знания
        if self.request.POST:
            context['zn_create_form'] = ZnForAlgorithmCreateUpdateForm(self.request.POST)
            context['rel_attr_form'] = RelationForZnInAlgorithm(parent_zn_tz=self.parent_zn_tz)
        else:
            context['zn_create_form'] = ZnForAlgorithmCreateUpdateForm(user=self.request.user)
            context['rel_attr_form'] = RelationForZnInAlgorithm(parent_zn_tz=self.parent_zn_tz)
        return context

    def post(self, request, *args, **kwargs):
        """Обрабатывает POST запрос"""
        self.object = None
        self.parent_id = self.kwargs.get('parent_id')
        # Получаем форму для заполнения данных Знания
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        print(self.request.POST)
        rel_attr_form = RelationForZnInAlgorithm(data=self.request.POST, parent_zn_tz=self.request.POST.get('tr'))
        print(rel_attr_form)
        if form.is_valid() and rel_attr_form.is_valid():
            print('mekroe')
            # tr = rel_attr_form.cleaned_data['tr']
            # knowledge = form.save(commit=False)
            # create_zn_for_constructor(knowledge, form, request)
            # create_relation(self.parent_id, knowledge.id, tr, request)
            return render(request, 'drevo/algorithm_constructor/zn_and_rel_for_algorithm_create.html', {
                'new': True,
                # 'new_knowledge': knowledge,
            })

        return self.form_invalid(form, rel_attr_form)

    def form_invalid(self, form, rel_attr_form):
        return self.render_to_response(self.get_context_data(form=form, rel_attr_form=rel_attr_form))


@require_http_methods(['GET'])
def get_tz_for_zn_in_algorithm(request):
    bz_id = request.GET.get('bz_id')
    tr_id = request.GET.get('tr_id')

    base_knowledge_tz_id = get_object_or_404(Znanie, pk=bz_id).tz_id

    req_relationship = (
        RelationshipTzTr.objects
        .filter(Q(base_tz_id=base_knowledge_tz_id) & Q(rel_type_id=tr_id))
        .values('rel_tz_id', 'rel_tz__name')
        .distinct()
    )

    if not req_relationship:
        JsonResponse(data={})

    res_data = {'tz': [{'id': rz.get('rel_tz_id'), 'name': rz.get('rel_tz__name')} for rz in req_relationship]}
    return JsonResponse(data=res_data)


def check_algorithm_correctness():
    names_of_errors = {
        'required_relation': 'Нет обязательной связи',
        'condition': 'У знания вида <Условие> отсутствует связь <Тогда>/<Если>',
        'not_only_rel': 'Связь не является единственной',

    }

