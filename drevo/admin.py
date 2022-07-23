from django.contrib import admin
from django.db.models import Q
from django.shortcuts import get_object_or_404

from drevo.models.expert_category import CategoryExpert
from .forms.relation_form import RelationAdminForm
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
)
from mptt.admin import DraggableMPTTAdmin

from django.utils.safestring import mark_safe
from django.utils.html import format_html
from adminsortable2.admin import SortableAdminMixin
from drevo.models.knowledge_grade_scale import KnowledgeGradeScale
from drevo.models.relation_grade_scale import RelationGradeScale
from drevo.models.knowledge_grade import KnowledgeGrade
from drevo.models.relation_grade import RelationGrade
from drevo.models import InterviewAnswerExpertProposal

from .forms import (
    ZnanieForm,
    AuthorForm,
    GlossaryTermForm,
    CategoryForm,
    CtegoryExpertForm,
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
    ]


admin.site.register(Tr, TrAdmin)


class TzAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = (
        "name",
        "order",
        "is_systemic",
        "is_group",
        "can_be_rated",
    )
    sortable_by = (
        "name",
        "is_systemic",
    )
    ordering = [
        "order",
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
        kwargs['form'] = RelationAdminForm
        return super().get_form(request, obj, change, **kwargs)

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        send_flag = form.cleaned_data.get('send_flag')
        name = form.cleaned_data.get('bz')
        super().save_model(request, obj, form, change)

        if send_flag:
            interview = get_object_or_404(Znanie, name=name)
            period = Relation.objects.filter(Q(bz=interview) & Q(tr__name='Период интервью')).first()
            if period:
                period_relation = period.rz.name.split('-')
                # Передаем параметры в функцию send_notify_interview, которая формирует текст сообщения
                result = send_notify_interview(interview, period_relation)

    class Media:
        css = {"all": ("drevo/css/style.css",)}
        js = ("drevo/js/notify_interview.js",)


admin.site.register(Relation, RelationAdmin)


class GlossaryTermAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    ordering = ("name",)

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
        "value",
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


@admin.register(InterviewAnswerExpertProposal)
class InterviewExpertResultAdmin(admin.ModelAdmin):
    exclude = ("updated",)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
