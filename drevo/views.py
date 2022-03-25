from django.db.models import Count, Q
from django.http import Http404, JsonResponse
from django.views.generic import ListView, TemplateView, DetailView
from django.views.generic.edit import ProcessFormView
from .models import Category, Znanie, Relation, Tr, Author, AuthorType, Label, GlossaryTerm, ZnRating, IP
from .forms import AuthorsFilterForm
from loguru import logger
from .relations_tree import get_category_for_knowledge, get_ancestors_for_knowledge, \
    get_siblings_for_knowledge, get_children_for_knowledge, get_knowledges_by_categories, \
    get_children_by_relation_type_for_knowledge
import collections
import humanize

logger.add('logs/main.log', format="{time} {level} {message}", rotation='100Kb', level="ERROR")


class DrevoListView(ListView):
    """
    выводит сущности Знание для заданной рубрики
    """
    template_name = 'drevo/type.html'
    model = Znanie
    context_object_name = 'znanie'

    def get_queryset(self):
        """
        формирует выборку из сущностей Знание для вывода
        """
        category_pk = self.kwargs['pk']
        qs = Znanie.published.filter(category__pk=category_pk).order_by('-order')
        return qs

    def get_context_data(self, *, object_list=None, **kwargs):
        """
        Передает данные в шаблон
        """
        context = super().get_context_data(**kwargs)
        # текущая категория
        category = Category.published.get(pk=self.kwargs['pk'])
        context['category'] = category
        return context


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
        zn = Znanie.published.all()
        zn_dict = {}
        for category in categories:
            zn_in_this_category = zn.filter(category=category).order_by('-order')
            zn_dict[category.name] = zn_in_this_category
        context['zn_dict'] = zn_dict

        return context


class ZnanieDetailView(DetailView):
    """
    Выводит подробную информацию о сущности Знание
    """
    model = Znanie
    context_object_name = 'znanie'
    template_name = 'drevo/znanie_detail.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        """
        Передает в шаблон данные через контекст
        """
        context = super().get_context_data(**kwargs)

        # первичный ключ текущей записи
        pk = self.object.pk

        # получаем список связей, в который базовым знанием является текущее знание
        qs = Relation.objects.filter(bz__pk=pk)

        # получаем список всех видов связей
        ts = Tr.objects.all()

        context['rels'] = [[item.name, qs.filter(tr=item, rz__is_published=True)]
                           for item in ts if qs.filter(tr=item, rz__is_published=True).count() > 0]

        # сохранение ip пользователя
        knowledge = Znanie.objects.get(pk=pk)
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        if IP.objects.filter(ip=ip).count() == 0:
            IP(ip=ip).save()

        IP.objects.get(ip=ip).visits.add(knowledge)

        IP.objects.get(ip=ip).save()

        # формируем дерево категорий для категории текущего знания
        category = get_category_for_knowledge(knowledge)
        if category:
            categories = category.get_ancestors(ascending=False, include_self=True)
        else:
            categories = []
        context['category'] = category
        context['categories'] = categories
        context['chain'] = get_ancestors_for_knowledge(knowledge)
        context['siblings'] = get_siblings_for_knowledge(knowledge)
        # context['children'] = get_children_for_knowledge(knowledge)
        context['children_by_tr'] = get_children_by_relation_type_for_knowledge(knowledge)
        context['visits'] = knowledge.ip_set.all().count()

        user = self.request.user
        if user.is_authenticated:
            user_vote = knowledge.get_users_vote(user)
            if user_vote:
                context['user_vote'] = {user_vote: True}

        context['likes_count'] = humanize.intword(knowledge.get_likes_count())
        context['dislikes_count'] = humanize.intword(knowledge.get_dislikes_count())

        return context


class LabelsListView(ListView):
    """
    выводит список меток
    """
    template_name = 'drevo/labels.html'
    model = Label
    context_object_name = 'labels'
    queryset = Label.objects.annotate(zn_num=Count('znanie',
                                                   filter=Q(znanie__is_published=True))).\
        all().order_by('name')


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
        context['categories'], context['knowledges'] = \
            get_knowledges_by_categories(knowledges_of_label)

        for z in knowledges_of_label:
            logger.debug(z.labels)

        return context


class AuthorsListView(ListView):
    """
    выводит список авторов
    """
    template_name = 'drevo/authors_list.html'
    model = Author
    context_object_name = 'authors'

    def get_queryset(self):
        """
        Возвращает queryset авторов в соответствии с фильтром, полученным из формы
        на странице со списком авторов
        """

        # получаем значение фильтра из запроса
        author_type_to_filter = self.request.GET.get('author_type')

        queryset = Author.objects.annotate(zn_num=Count('znanie', filter=Q(znanie__is_published=True))).all().order_by('name')

        # валидируем значение и возвращаем queryset
        list_of_author_types = AuthorType.objects.all().values_list('id', flat=True)
        if author_type_to_filter not in list(map(str, list_of_author_types)):
            return queryset
        else:
            return queryset.filter(atype=author_type_to_filter)

    def get_context_data(self, *, object_list=None, **kwargs):
        """
        Контекст, передаваемый в шаблон
        """
        context = super().get_context_data(**kwargs)

        rform = AuthorsFilterForm(self.request.GET)
        rform.is_valid()
        context['rform'] = rform

        return context


class AuthorDetailView(DetailView):
    """
    Выводит подробную информацию об Авторе
    """
    model = Author
    context_object_name = 'author'
    template_name = 'drevo/author_details.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        """
        Контекст, передаваемый в шаблон
        """
        context = super().get_context_data(**kwargs)

        # получаем знания данного автора
        knowledges_of_author = Znanie.published.filter(author__id=int(self.kwargs['pk']))

        context['categories'], context['knowledges'] = \
            get_knowledges_by_categories(knowledges_of_author)

        return context


class GlossaryListView(ListView):
    """
    выводит список терминов глоссария
    """
    template_name = 'drevo/glossary.html'
    model = GlossaryTerm
    context_object_name = 'glossary_terms'
    queryset = GlossaryTerm.objects.filter(is_published=True)


class ZnanieRatingView(ProcessFormView):
    def get(self, request, pk, vote, *args, **kwargs):
        if request.is_ajax():
            if not self.request.user.is_authenticated:
                return JsonResponse({}, status=403)

            if pk and vote:
                if vote in (ZnRating.LIKE, ZnRating.DISLIKE):
                    znanie = Znanie.objects.get(pk=pk)
                    znanie.voting(self.request.user, vote)
                    return JsonResponse({}, status=200)

        raise Http404
