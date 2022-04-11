from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.http import Http404, JsonResponse
from django.views.generic import ListView, TemplateView, DetailView
from django.views.generic.edit import ProcessFormView
from .models import Category, Znanie, Relation, Tr, Author, AuthorType, Label, GlossaryTerm, ZnRating, IP, Visits, \
    Comment
from users.models import User
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
        if not IP.objects.filter(ip=ip):
            IP.objects.create(ip=ip)
        if knowledge not in IP.objects.get(ip=ip).visits.all() and self.request.user.is_anonymous:
            IP.objects.get(ip=ip).visits.add(knowledge)

        IP.objects.get(ip=ip).save()

        # добавление просмотра
        if self.request.user.is_authenticated:
            if not Visits.objects.filter(znanie=knowledge, user=self.request.user).count():
                Visits.objects.create(znanie=knowledge, user=self.request.user).save()

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
        context['visits'] = Visits.objects.filter(znanie=knowledge).count() + knowledge.ip_set.all().count()

        user = self.request.user
        if user.is_authenticated:
            user_vote = knowledge.get_users_vote(user)
            if user_vote:
                context['user_vote'] = {user_vote: True}

        context['likes_count'] = humanize.intword(knowledge.get_likes_count())
        context['dislikes_count'] = humanize.intword(knowledge.get_dislikes_count())
        context['comment_max_length'] = Comment.CONTENT_MAX_LENGTH

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


class CommentPageView(ProcessFormView):
    def get(self, request, pk, *args, **kwargs):
        if request.is_ajax():
            if pk:
                offset = Comment.COMMENTS_PER_PAGE
                is_last_page = False
                is_first_page = True

                last_comment_id = request.GET.get('last_comment_id')
                if last_comment_id:
                    if last_comment_id.isdigit():
                        last_comment_id = int(last_comment_id)
                    else:
                        raise Http404
                else:
                    last_comment_id = None

                znanie = get_object_or_404(Znanie, id=pk)

                if last_comment_id:
                    comments = znanie.comments.filter(
                        parent=None,
                        id__lt=int(last_comment_id),
                    ).select_related('parent', 'author')[0:offset]
                else:
                    comments = znanie.comments.filter(
                        parent=None,
                    ).select_related('parent', 'author')[0:offset]

                if not comments:
                    return JsonResponse(
                        {'data': render_to_string('drevo/comments_list.html'), 'is_last_page': True},
                        status=200
                    )

                if znanie.comments.filter(parent=None).last() in comments:
                    is_last_page = True
                if last_comment_id:
                    is_first_page = False

                context = {
                    'comments': comments,
                    'comment_max_length': Comment.CONTENT_MAX_LENGTH,
                    'is_authenticated': self.request.user.is_authenticated,
                    'offset': offset,
                    'is_first_page': is_first_page,
                    'is_last_page': is_last_page,
                }

                data = render_to_string('drevo/comments_list.html', context)
                return JsonResponse({'data': data, 'is_last_page': is_last_page}, status=200)

        raise Http404


class CommentSendView(ProcessFormView):
    def get(self, request, pk, *args, **kwargs):
        if request.is_ajax():
            user = self.request.user

            if not user.is_authenticated:
                return JsonResponse({}, status=403)

            if pk:
                parent_id = self.request.GET.get('parent')
                content = self.request.GET.get('content').strip()

                if not content:
                    raise Http404

                znanie = get_object_or_404(Znanie, id=pk)
                author = get_object_or_404(User, id=user.id)
                parent_comment = None
                if parent_id:
                    parent_comment = get_object_or_404(Comment, id=parent_id)

                new_comment = Comment.objects.create(
                    author=author,
                    parent=parent_comment,
                    znanie=znanie,
                    content=content,
                )
                context = {
                    'is_authenticated': user.is_authenticated,
                    'comment_max_length': Comment.CONTENT_MAX_LENGTH,
                }

                is_first_answer = True
                if parent_id and parent_comment.answers.count() > 1:
                    is_first_answer = False

                if parent_id and not is_first_answer:
                    context['comment'] = new_comment
                    data = render_to_string('drevo/comments_card.html', context)
                else:
                    context['comments'] = [new_comment]
                    data = render_to_string('drevo/comments_list.html', context)

                return JsonResponse(
                    {
                        'data': data,
                        'new_comment_id': new_comment.id,
                        'is_first_answer': is_first_answer
                    },
                    status=200
                )

        raise Http404
