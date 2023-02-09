from adminsortable2.admin import SortableAdminMixin
from django.contrib import admin
from django.db.models import Q
from django.db.models.functions import Lower
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from mptt.admin import DraggableMPTTAdmin

from drevo.models import InterviewAnswerExpertProposal
from drevo.models.expert_category import CategoryExpert
from drevo.models.knowledge_grade import KnowledgeGrade
from .forms.relation_form import RelationAdminForm
from drevo.models.knowledge_grade_scale import KnowledgeGradeScale
from drevo.models.relation_grade import RelationGrade
from drevo.models.relation_grade_scale import RelationGradeScale
from drevo.models.friends_invite import FriendsInviteTerm
from drevo.models.label_feed_message import LabelFeedMessage
from drevo.models.feed_messages import FeedMessage, LabelFeedMessage
from drevo.models.developer import Developer
from drevo.models.quiz_results import QuizResult
from drevo.models.message import Message

from .forms.developer_form import DeveloperForm
from .forms import (
    ZnanieForm,
    AuthorForm,
    GlossaryTermForm,
    CategoryForm,
    CtegoryExpertForm,
)
from .models import (
    Znanie,
    Tz,
    Author,
    Label,
    Tr,
    Relation,
    Category,
    ZnImage,
    AuthorType,
    GlossaryTerm,
    ZnRating,
    Comment,
    KnowledgeStatuses,
    AgeUsersScale,
    InterviewResultsSendingSchedule,
    SettingsOptions,
    UserParameters,
    ParameterCategories
)
from .services import send_notify_interview


class CategoryMPTT(DraggableMPTTAdmin):
    search_fields = ["name"]
    list_display = (
        "tree_actions",
        "indented_title_ispublished",
    )
    list_display_links = ("indented_title_ispublished",)

    def get_form(self, request, obj=None, **kwargs):
        kwargs["form"] = CategoryForm
        return super().get_form(request, obj, **kwargs)

    def indented_title_ispublished(self, instance):
        published_str = "published" if instance.is_published else "unpublished"
        return format_html(
            '<div style="text-indent:{}px" class="{}">{}</div>',
            instance._mpttfield("level") * self.mptt_level_indent,
            published_str,
            instance.name,  # Or whatever you want to put here
        )

    indented_title_ispublished.short_description = "Категория"

    class Media:
        css = {"all": ("drevo/css/style.css",)}


admin.site.register(Category, CategoryMPTT)


class LabelAdmin(admin.ModelAdmin):
    list_display = ("name",)
    ordering = ("name",)
    search_fields = ["name"]

    class Media:
        css = {"all": ("drevo/css/style.css",)}


admin.site.register(Label, LabelAdmin)


class ZnImageInline(admin.StackedInline):
    """
    Класс для "встраивания" формы добавления фотографий в форму создания Знания
    """

    model = ZnImage
    extra = 3
    verbose_name_plural = "фотографии"
    verbose_name = "фото"

    def photo_out(self, obj):
        """
        Выводит фото вместо текста ссылки
        """
        return mark_safe(f'<a href="{obj.href}">источник</a>')

    photo_out.short_description = "Миниатюра"


class ZnanieAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order",
        "name",
        "tz",
        "href2link",
        "author",
        "updated_at",
        "user",
        "is_send",
    )
    list_display_links = ("id", "name")
    ordering = ("order",)
    save_as = True
    autocomplete_fields = ["labels", "category", "author"]
    search_fields = ["name"]
    list_filter = (
        "tz",
        "author",
        "updated_at",
        "is_published",
        "labels",
    )
    list_per_page = 30
    inlines = [
        ZnImageInline,
    ]
    exclude = ("visits",)

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        super().save_model(request, obj, form, change)

    def get_form(self, request, obj=None, **kwargs):
        kwargs["form"] = ZnanieForm
        return super().get_form(request, obj, **kwargs)

    def href2link(self, obj):
        """
        Выводит ссылку вместо текста в поле href
        """
        if obj.href:
            return mark_safe(f'<a href="{obj.href}">источник</a>')
        else:
            return ""

    href2link.short_description = "Ссылка"

    def change_view(self, request, object_id, form_url="", extra_context=None):
        """
        Изменяет заголовок в форме редактирования объекта, см. https://docs.djangoproject.com/en/3.2/ref/contrib/admin/#django.contrib.admin.ModelAdmin.change_view

        Контекстные переменные см. шаблон https://github.com/django/django/blob/main/django/contrib/admin/templates/admin/change_form.html
        а также шаблоны-родители base_site.html и base.html.
        Контекстная переменная subtitle прописана именно в base.html.
        """
        extra_context = extra_context or {}
        # Получаем объект Znanie с соотв. id
        z = Znanie.objects.get(id=object_id)
        extra_context["subtitle"] = f"{z.pk} - {z.name}"
        return super().change_view(
            request,
            object_id,
            form_url,
            extra_context=extra_context,
        )

    class Media:
        css = {"all": ("drevo/css/style.css",)}


admin.site.register(Znanie, ZnanieAdmin)


class AuthorAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "atype",
        "user_author",
    )
    ordering = ("name",)
    search_fields = ["name"]
    list_filter = ("atype",)

    def get_form(self, request, obj=None, **kwargs):
        kwargs["form"] = AuthorForm
        return super().get_form(request, obj, **kwargs)

    class Media:
        css = {"all": ("drevo/css/style.css",)}


admin.site.register(Author, AuthorAdmin)


class AuthorTypeAdmin(admin.ModelAdmin):
    list_display = ("name",)
    ordering = ("name",)


admin.site.register(AuthorType, AuthorTypeAdmin)


class TrAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = (
        "name",
        "order",
        "is_systemic",
        "is_argument",
        "argument_type",
    )
    sortable_by = (
        "name",
        "is_systemic",
    )
    ordering = [
        "order",
        "name",
    ]


admin.site.register(Tr, TrAdmin)


class TzAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = (
        "name",
        "order",
        "is_systemic",
        "is_group",
        "can_be_rated",
        "is_send",
    )
    sortable_by = (
        "name",
        "is_systemic",
    )
    ordering = [
        "order",
        "name",
    ]


admin.site.register(Tz, TzAdmin)


class RelationAdmin(admin.ModelAdmin):
    list_display = ("id", "bz", "tr", "rz", "author", "date", "user")
    save_as = True
    autocomplete_fields = ["bz", "rz", "author"]
    search_fields = ["bz__name", "rz__name"]
    list_filter = (
        "tr",
        "author",
        "date",
        "is_published",
    )
    ordering = ("-date",)

    def get_form(self, request, obj=None, change=False, **kwargs):
        kwargs["form"] = RelationAdminForm
        return super().get_form(request, obj, change, **kwargs)

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        send_flag = form.cleaned_data.get("send_flag")
        name = form.cleaned_data.get("bz")
        super().save_model(request, obj, form, change)

        if send_flag:
            interview = get_object_or_404(Znanie, name=name)
            period = Relation.objects.filter(
                Q(bz=interview) & Q(tr__name="Период интервью")
            ).first()
            if period:
                period_relation = period.rz.name
                # Передаем параметры в функцию send_notify_interview, которая формирует текст сообщения
                result = send_notify_interview(interview, period_relation)

    class Media:
        css = {"all": ("drevo/css/style.css",)}
        js = ("drevo/js/notify_interview.js",)


admin.site.register(Relation, RelationAdmin)


class GlossaryTermAdmin(admin.ModelAdmin):
    list_display = ("order", "name", "description")
    ordering = ("order", "name",)
    list_display_links = ('name',)

    def get_form(self, request, obj=None, **kwargs):
        kwargs["form"] = GlossaryTermForm
        return super().get_form(request, obj, **kwargs)


admin.site.register(GlossaryTerm, GlossaryTermAdmin)


class ZnRatingAdmin(admin.ModelAdmin):
    list_display = ("znanie", "user", "value", "created_at", "updated_at")
    readonly_fields = ("znanie", "user", "value", "created_at", "updated_at")
    list_filter = ("value", "znanie")


admin.site.register(ZnRating, ZnRatingAdmin)


class CommentAnswersInline(admin.TabularInline):
    model = Comment
    ordering = ("-created_at",)
    extra = 0
    readonly_fields = (
        "author",
        "parent",
        "znanie",
        "content",
        "created_at",
        "updated_at",
        "is_published",
    )
    can_delete = False
    verbose_name = "Ответ"
    verbose_name_plural = "Ответы"


class CommentAdmin(admin.ModelAdmin):
    readonly_fields = (
        "author",
        "parent",
        "znanie",
        "content",
        "created_at",
        "updated_at",
    )
    list_filter = ("is_published", "created_at", "znanie", "author")
    ordering = ("-created_at",)
    inlines = (CommentAnswersInline,)
    verbose_name = "Комментарий"
    verbose_name_plural = "Комментарии"


admin.site.register(Comment, CommentAdmin)


class QuizResultAdmin(admin.ModelAdmin):
    readonly_fields = (
        "quiz",
        "question",
        "answer",
        "user",
        "date_time",
    )

    verbose_name = 'Результаты теста'
    verbose_name_plural = 'Результаты тестов'


admin.site.register(QuizResult, QuizResultAdmin)


class KnowledgeGradeScaleAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "low_value",
        "is_low_in_range",
        "high_value",
        "is_high_in_range",
    )


admin.site.register(KnowledgeGradeScale, KnowledgeGradeScaleAdmin)


class RelationGradeScaleAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "low_value",
        "is_low_in_range",
        "high_value",
        "is_high_in_range",
    )


admin.site.register(RelationGradeScale, RelationGradeScaleAdmin)


class KnowledgeGradeAdmin(admin.ModelAdmin):
    list_display = (
        "knowledge",
        "user",
        "grade",
        "created_at",
    )
    list_filter = ("grade", "created_at", "knowledge")
    autocomplete_fields = ("knowledge",)


admin.site.register(KnowledgeGrade, KnowledgeGradeAdmin)


class RelationGradeAdmin(admin.ModelAdmin):
    list_display = (
        "relation",
        "user",
        "grade",
        "created_at",
    )
    list_filter = ("grade", "created_at", "relation")


admin.site.register(RelationGrade, RelationGradeAdmin)


class CategoryExpertAdmin(admin.ModelAdmin):
    list_display = ("expert", "get_categories")
    fields = ("expert", "categories")

    def get_categories(self, obj):
        """
        Собирает категории экспертов в список по порядку id
        """
        list_categories = []
        for category_expert in obj.categories.all():
            list_categories.append(category_expert.name)
        list_categories = list(set(list_categories))
        return ",\n".join(list_categories)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields["categories"] = CtegoryExpertForm.base_fields["category"]
        form.base_fields["categories"].label = "Компетенции"
        return form

    class Media:
        css = {"all": ("drevo/css/style.css",)}


admin.site.register(CategoryExpert, CategoryExpertAdmin)


class InterviewInline(admin.TabularInline):
    model = Znanie


class InterviewFilter(admin.SimpleListFilter):
    title = 'Интервью'
    parameter_name = 'interview'

    def lookups(self, request, model_admin):
        return [(inter.id, inter.name) for inter in Znanie.objects.select_related('tz').filter(tz__name='Интервью')]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(interview__id=self.value())
        return queryset


class QuestionFilter(admin.SimpleListFilter):
    title = 'Вопрос'
    parameter_name = 'question'

    def lookups(self, request, model_admin):
        return [(quest.id, quest.name) for quest in Znanie.objects.select_related('tz').filter(tz__name='Вопрос')]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(question__id=self.value())
        return queryset


@admin.register(InterviewAnswerExpertProposal)
class InterviewAnswerExpertProposalAdmin(admin.ModelAdmin):
    exclude = ("updated",)
    autocomplete_fields = ("interview", "answer", "question")
    # тут мы ссылаемся на методы *_link, чтобы соответствующие Знания были показаны ссылками в списке всех Proposal
    list_display = (
        "id",
        "interview_link",
        "question_link",
        "answer_link",
        "new_answer_text",
        "admin_reviewer",
        "status",
        "is_notified"
    )
    list_display_links = ("id",)
    list_filter = (InterviewFilter, QuestionFilter)

    @staticmethod
    def link_to_knowledge_change(obj):
        """Превращаем поле в ссылку в админке"""
        if obj is None:
            return "-"
        title = obj.name
        if len(title) > 50:
            title = f'{title[:50]}...'
        return format_html(
            "<a href='{url}'>{title}</a>",
            url=reverse("admin:drevo_znanie_change", args=(obj.id,)),
            title=title,
        )

    def interview_link(self, obj):
        return self.link_to_knowledge_change(obj.interview)

    def question_link(self, obj):
        return self.link_to_knowledge_change(obj.question)

    def answer_link(self, obj):
        return self.link_to_knowledge_change(obj.answer)


class DeveloperAdmin(admin.ModelAdmin):
    list_display = ("name", "surname", "contribution", "comment", "admin")
    fields = ("name", "surname", "contribution", "comment", "admin")

    def get_form(self, request, obj=None, **kwargs):
        kwargs["form"] = DeveloperForm
        return super().get_form(request, obj, **kwargs)


admin.site.register(Developer, DeveloperAdmin)


@admin.register(InterviewResultsSendingSchedule)
class InterviewResultsSendingScheduleAdmin(admin.ModelAdmin):
    list_display = ['id', 'interview', 'next_sending', 'last_sending']
    readonly_fields = ['interview']

    def has_add_permission(self, request, obj=None):
        return False


admin.site.register(FriendsInviteTerm)
admin.site.register(LabelFeedMessage)
admin.site.register(FeedMessage)
admin.site.register(Message)
admin.site.register(AgeUsersScale)


@admin.register(KnowledgeStatuses)
class KnowledgeStatusesAdmin(admin.ModelAdmin):
    list_display = ('knowledge', 'status', 'user', 'time_limit', 'is_active',)
    autocomplete_fields = ['knowledge']
    search_fields = ['knowledge__name']


@admin.register(SettingsOptions)
class SettingsOptionsAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'category', 'default_param', 'admin']
    search_fields = ['name']
    list_display_links = ['id']
    list_filter = ['category', 'admin']


@admin.register(UserParameters)
class UserParametersAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'param', 'param_value']
    list_display_links = ['id']


@admin.register(ParameterCategories)
class ParameterCategoriesAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']
    list_display_links = ['id']
