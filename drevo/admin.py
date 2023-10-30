from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from adminsortable2.admin import SortableAdminMixin
from django.conf.urls import url
from django.contrib import admin
from django.db import IntegrityError
from django.db.models import Q, F
from django.db.models.functions import Lower
from django.forms.models import model_to_dict
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from mptt.admin import DraggableMPTTAdmin

from drevo.models import InterviewAnswerExpertProposal
from drevo.models.special_permissions import SpecialPermissions
from drevo.models.knowledge_grade import KnowledgeGrade
from .forms.relation_form import RelationAdminForm
from drevo.models.knowledge_grade_scale import KnowledgeGradeScale
from drevo.models.knowledge_grade_color import KnowledgeGradeColor
from drevo.models.relation_grade import RelationGrade
from drevo.models.relation_grade_scale import RelationGradeScale
from drevo.models.friends_invite import FriendsInviteTerm
from drevo.models.label_feed_message import LabelFeedMessage
from drevo.models.feed_messages import FeedMessage, LabelFeedMessage
from drevo.models.developer import Developer
from drevo.models.quiz_results import QuizResult
from drevo.models.message import Message
from drevo.models import QuestionToKnowledge
from drevo.models import UserAnswerToQuestion

from drevo.models.suggestion import Suggestion
from drevo.models.suggestion_type import SuggestionType
from drevo.models.refuse_reason import RefuseReason


from .forms.developer_form import DeveloperForm
from .forms.admin_user_suggestion_form import AdminSuggestionUserForm
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
    ZnFile,
    AuthorType,
    GlossaryTerm,
    ZnRating,
    Comment,
    KnowledgeStatuses,
    AgeUsersScale,
    InterviewResultsSendingSchedule,
    SettingsOptions,
    UserParameters,
    ParameterCategories,
    SubAnswers,
    RelationshipTzTr,
    RelationStatuses,
    QuestionToKnowledge,
    UserAnswerToQuestion
)
from .models.algorithms_data import AlgorithmData
from .models.appeal import Appeal
from .services import send_notify_interview
from .views.send_email_message import send_email_messages


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


class ZnFileInline(admin.StackedInline):
    """
    Класс для "встраивания" формы добавления файлов в форму создания Знания
    """

    model = ZnFile
    extra = 1
    verbose_name_plural = "Файлы"
    verbose_name = "Файл"

    def files_out(self, obj):
        """
        Выводит фото вместо текста ссылки
        """
        return mark_safe(f'<a href="{obj.href}">источник</a>')

    files_out.short_description = "Файл"


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
        ZnFileInline
    ]
    exclude = ("visits",)
    change_list_template = "admin/drevo/knowledge/change_list.html"

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

    def get_urls(self):
        urls = super(ZnanieAdmin, self).get_urls()
        custom_urls = [url('^send_email_messages/$', self.process_sending, name='process_sending'), ]
        return custom_urls + urls

    def process_sending(self, request):
        sending_emails = send_email_messages()
        if str(sending_emails).endswith('1'):
            mail = 'письмо'
        elif str(sending_emails).endswith('2') or str(sending_emails).endswith('3') or str(sending_emails).endswith('4'):
            mail = 'письма'
        else:
            mail = 'писем'
        self.message_user(request, f"Отправлено {sending_emails} {mail}!")
        return HttpResponseRedirect("../")

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


@admin.register(Tr)
class TrAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = (
        "name",
        "order",
        "is_systemic",
        "is_argument",
        "argument_type",
        "has_invert",
    )
    sortable_by = (
        "name",
        "is_systemic",
    )
    ordering = [
        "order",
        "name",
    ]


class TzAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = (
        "name",
        "tr",
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


@admin.register(Relation)
class RelationAdmin(admin.ModelAdmin):
    list_display = ("id", "bz", "tr", "rz", "author", "date", "user", "expert", "director", "order")
    save_as = True
    autocomplete_fields = ["author"]
    search_fields = ["bz__name", "rz__name"]
    list_filter = (
        "tr",
        "author",
        "date",
        "is_published",
    )
    ordering = ("-date",)
    form = RelationAdminForm

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            if obj.tr.has_invert:
                Relation.objects.filter(bz=obj.rz, rz=obj.bz, tr=obj.tr.invert_tr).delete()
                obj.delete()
            else:
                obj.delete()

    def change_view(self, request, object_id, form_url="", extra_context=None):
        response = super().change_view(request, object_id, form_url, extra_context)
        obj = self.get_object(request, object_id)
        if obj.tr.has_invert:
            """
            При изменении объекта, у которого есть инверсная модель,
            изменения сохраняются и в объект, и в инверсной модели.
            """
            fields = model_to_dict(obj, exclude=('id', 'bz', 'rz', 'tr'))
            invert_obj = get_object_or_404(Relation, bz=obj.rz, rz=obj.bz, tr=obj.tr.invert_tr)
            for f_name in fields:
                setattr(invert_obj, f_name, getattr(obj, f_name))
            invert_obj.save()

        return response

    def delete_view(self, request, object_id, extra_context=None):
        """
        Если у объекта есть инвертная модель, удаляется сам объект,
        и его инверсная модель.
        """
        obj = self.get_object(request, object_id)
        if obj.tr.has_invert:
            Relation.objects.filter(bz=obj.rz, rz=obj.bz, tr=obj.tr.invert_tr).delete()
        return super().delete_view(request, object_id, extra_context)

    def save_model(self, request, obj, form, change):
        data = form.cleaned_data
        obj.user = request.user
        send_flag = data.get("send_flag")
        name = data.get("bz")
        super().save_model(request, obj, form, change)

        if obj.tr.has_invert:
            """
            Если у объекта Tr указано поле 'invert_relation',
            тогда меняем местами значения полей 'bz' и 'rz',
            а поле 'tr' меняем на инверсную модель Tr и сохраняем
            дополнительную инверсную связь.
            """
            data['bz'], data['rz'], data['tr'] = data['rz'], data['bz'], obj.tr.invert_tr
            data.pop('send_flag')
            try:
                Relation.objects.get_or_create(**data, user=request.user)
            except IntegrityError:
                pass

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
        # css = {"all": ("drevo/css/style.css",)}
        js = ("drevo/js/notify_interview.js",)


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
        "order",
    )


admin.site.register(KnowledgeGradeScale, KnowledgeGradeScaleAdmin)


class KnowledgeGradeColorAdmin(admin.ModelAdmin):
    list_display = (
        "hue",
        "saturation",
        "high_light",
        "low_light",
        "knowledge_type",
    )

admin.site.register(KnowledgeGradeColor, KnowledgeGradeColorAdmin)


class RelationGradeScaleAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "low_value",
        "is_low_in_range",
        "high_value",
        "is_high_in_range",
        "order",
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


@admin.register(SpecialPermissions)
class SpecialPermissionsAdmin(admin.ModelAdmin):
    list_display = ("pk", "expert", "get_categories", "get_admin_competencies", "editor")
    list_filter = ('editor',)
    search_fields = ('expert',)
    save_as = True

    def get_categories(self, obj):
        """
        Собирает категории экспертов в список по порядку id
        """
        list_categories = []
        for category_expert in obj.categories.all():
            list_categories.append(category_expert.name)
        list_categories = list(set(list_categories))
        return ",\n".join(list_categories)

    def get_admin_competencies(self, obj):
        """
        Собирает категории, которые входят в список компетенций руководителя у экспертов
        """
        return ', \n'.join(obj.admin_competencies.values_list('name', flat=True))

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields["categories"] = CtegoryExpertForm.base_fields["category"]
        form.base_fields["categories"].label = "Компетенции эксперта"
        form.base_fields["admin_competencies"] = CtegoryExpertForm.base_fields['admin_competencies']
        form.base_fields["admin_competencies"].label = 'Компетенции руководителя'
        return form

    get_categories.short_description = 'Компетенции эксперта'
    get_admin_competencies.short_description = 'Компетенции руководителя'

    class Media:
        css = {"all": ("drevo/css/style.css",)}


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
        interview_questions = (
            Relation.objects
            .select_related('rz', 'bz')
            .filter(
                bz__tz_id=get_object_or_404(Tz, name='Интервью').id,
                rz__tz_id=get_object_or_404(Tz, name='Вопрос').id
            )
            .values(question_pk=F('rz_id'), question_name=F('rz__name'))
            .order_by().distinct()
        )
        return [(quest_data.get('question_pk'), quest_data.get('question_name')) for quest_data in interview_questions]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(question__id=self.value())
        return queryset


class ExpertsFilter(admin.SimpleListFilter):
    title = 'Ответивший эксперт'
    parameter_name = 'expert'

    def lookups(self, request, model_admin):
        experts_with_proposals = (
            InterviewAnswerExpertProposal.objects
            .select_related('expert')
            .values(expert_pk=F('expert_id'), expert_username=F('expert__username'))
            .order_by().distinct()
        )
        return [(expert.get('expert_pk'), expert.get('expert_username')) for expert in experts_with_proposals]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(expert__id=self.value())
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
        "incorrect_answer_explanation",
        "admin_reviewer",
        "status",
        "is_notified"
    )
    list_display_links = ("id",)
    list_filter = (InterviewFilter, QuestionFilter, ExpertsFilter)
    search_fields = (
        'interview__name',
        'question__name',
        'answer__name',
        'incorrect_answer_explanation',
        'new_answer_text',
    )

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
    fields = ("name", "surname", "contribution", "comment", "admin", "photo")

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
    list_display = ('knowledge', 'status', 'user', 'time_limit', 'is_active', 'created_at')
    autocomplete_fields = ['knowledge']
    search_fields = ['knowledge__name']


@admin.register(RelationStatuses)
class RelationStatusesAdmin(admin.ModelAdmin):
    list_display = ('relation', 'status', 'user', 'time_limit', 'is_active', 'created_at')
    autocomplete_fields = ('relation',)
    search_fields = ('relation__name',)
    list_filter = ('status',)
    save_as = True


@admin.register(SettingsOptions)
class SettingsOptionsAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'category', 'default_param', 'admin', 'is_bool']
    search_fields = ['name']
    list_display_links = ['id']
    list_filter = ['category', 'admin', 'is_bool']


@admin.register(UserParameters)
class UserParametersAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'param', 'param_value']
    list_display_links = ['id']


@admin.register(ParameterCategories)
class ParameterCategoriesAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']
    list_display_links = ['id']


@admin.register(SubAnswers)
class SubAnswersAdmin(admin.ModelAdmin):
    list_display = ('pk', 'expert', 'interview', 'question', 'answer', 'sub_answer')
    list_display_links = ('pk', 'expert')
    search_fields = ('interview', 'question', 'answer', 'expert')
    autocomplete_fields = ('interview', 'question', 'answer')
    save_as = True
    save_on_top = True


@admin.register(RelationshipTzTr)
class RelationshipTzTrAdmin(admin.ModelAdmin):
    list_display = ('pk', 'base_tz', 'rel_type', 'rel_tz', 'is_only_one_rel')
    search_fields = ('base_tz__name', 'rel_type__name', 'rel_tz__name')
    list_display_links = ('pk',)
    list_filter = ('base_tz', 'rel_type', 'rel_tz')
    save_as = True


@admin.register(Appeal)
class AppealAdmin(admin.ModelAdmin):
    list_display = ("user", "subject", "created_at", "admin")
    readonly_fields = ("created_at", "resolved")


@admin.register(AlgorithmData)
class AlgorithmDataAdmin(admin.ModelAdmin):
    list_display = ("user", "algorithm", "work_name")


@admin.register(QuestionToKnowledge)
class QuestionToKnowledgeAdmin(admin.ModelAdmin):
    list_display = (
        "knowledge",
        "order",
        "question",
        "publication",
        "need_file"
    )
    ordering = ["order"]
    search_fields = ["knowledge__name", "question"]
    list_filter = ["publication", "need_file"]
    list_display_links = ["question"]
    autocomplete_fields = ["knowledge"]

    class Media:
        css = {"all": ("drevo/css/width_form.css",)}


@admin.register(UserAnswerToQuestion)
class UserAnswerToQuestionAdmin(admin.ModelAdmin):
    list_display = (
        "knowledge",
        "question",
        "answer",
        "date",
        "user",
        "accepted",
    )
    search_fields = ["knowledge__name", "answer", "question__question"]
    list_display_links = ("knowledge", "answer")
    
    class Media:
        css = {"all": ("drevo/css/width_form.css",)}



@admin.register(Suggestion)
class UserSuggestionAdmin(admin.ModelAdmin):
    list_display = ('parent_knowlege', 'name', 'user', 'expert', 'is_approve', 'suggestions_type')
    list_filter = ('suggestions_type', 'user', 'parent_knowlege')
    form = AdminSuggestionUserForm


@admin.register(SuggestionType)
class SuggestionTypeAdmin(admin.ModelAdmin):
    list_display = ('type_name', 'weight')
    list_filter = ('type_name', 'weight')


@admin.register(RefuseReason)
class RefuseReasonAdmin(admin.ModelAdmin):
    pass
