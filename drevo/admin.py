from django.contrib import admin
from drevo.models import Znanie, Tz, Author, Label, Tr, Relation, Category, ZnImage, AuthorType, GlossaryTerm
from mptt.admin import DraggableMPTTAdmin
from .forms import ZnanieForm, AuthorForm, GlossaryTermForm, CategoryForm
from django.utils.safestring import mark_safe
from django.utils.html import format_html


class CategoryMPTT(DraggableMPTTAdmin):
    search_fields = ['name']
    list_display = (
        'tree_actions',
        'indented_title_ispublished',
    )
    list_display_links = (
        'indented_title_ispublished',
    )

    def get_form(self, request, obj=None, **kwargs):
        kwargs['form'] = CategoryForm
        return super().get_form(request, obj, **kwargs)

    def indented_title_ispublished(self, instance):
        published_str = 'published' if instance.is_published else 'unpublished'
        return format_html(
            '<div style="text-indent:{}px" class="{}">{}</div>',
            instance._mpttfield('level') * self.mptt_level_indent,
            published_str,
            instance.name,  # Or whatever you want to put here
        )

    indented_title_ispublished.short_description = 'Категория'

    class Media:
        css = {
            "all": ("drevo/css/style.css",)
        }


admin.site.register(Category, CategoryMPTT)


class LabelAdmin(admin.ModelAdmin):
    list_display = ('name', )
    ordering = ('name',)
    search_fields = ['name']

    class Media:
        css = {
            "all": ("drevo/css/style.css",)
        }


admin.site.register(Label, LabelAdmin)


class ZnImageInline(admin.StackedInline):
    """
    Класс для "встраивания" формы добавления фотографий в форму создания Знания
    """
    model = ZnImage
    extra = 3
    verbose_name_plural = 'фотографии'
    verbose_name = 'фото'

    def photo_out(self, obj):
        """
        Выводит фото вместо текста ссылки
        """
        return mark_safe(f'<a href="{obj.href}">источник</a>')
    photo_out.short_description = 'Миниатюра'


class ZnanieAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'name', 'tz', 'href2link', 'author', 'updated_at', 'user')
    list_display_links = ('id', 'name')
    ordering = ('order',)
    save_as = True
    autocomplete_fields = ['labels', 'category', 'author']
    search_fields = ['name']
    list_filter = ('tz', 'author', 'updated_at', 'is_published', 'labels', )
    list_per_page = 30
    inlines = [ZnImageInline, ]

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        super().save_model(request, obj, form, change)

    def get_form(self, request, obj=None, **kwargs):
        kwargs['form'] = ZnanieForm
        return super().get_form(request, obj, **kwargs)

    def href2link(self, obj):
        """
        Выводит ссылку вместо текста в поле href
        """
        if obj.href:
            return mark_safe(f'<a href="{obj.href}">источник</a>')
        else:
            return ''
    href2link.short_description = 'Ссылка'

    def change_view(self, request, object_id, form_url='', extra_context=None):
        """
        Изменяет заголовок в форме редактирования объекта, см. https://docs.djangoproject.com/en/3.2/ref/contrib/admin/#django.contrib.admin.ModelAdmin.change_view

        Контекстные переменные см. шаблон https://github.com/django/django/blob/main/django/contrib/admin/templates/admin/change_form.html
        а также шаблоны-родители base_site.html и base.html.
        Контекстная переменная subtitle прописана именно в base.html.
        """
        extra_context = extra_context or {}
        # Получаем объект Znanie с соотв. id
        z = Znanie.objects.get(id=object_id)
        extra_context['subtitle'] = f"{z.pk} - {z.name}"
        return super().change_view(
            request, object_id, form_url, extra_context=extra_context,
        )    

    class Media:
        css = {
            "all": ("drevo/css/style.css",)
        }


admin.site.register(Znanie, ZnanieAdmin)


class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name', 'atype', )
    ordering = ('name',)
    search_fields = ['name']
    list_filter = ('atype', )

    def get_form(self, request, obj=None, **kwargs):
        kwargs['form'] = AuthorForm
        return super().get_form(request, obj, **kwargs)

    class Media:
        css = {
            "all": ("drevo/css/style.css",)
        }


admin.site.register(Author, AuthorAdmin)


class AuthorTypeAdmin(admin.ModelAdmin):
    list_display = ('name', )
    ordering = ('name',)


admin.site.register(AuthorType, AuthorTypeAdmin)


class TrAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_systemic', )
    ordering = ('name',)


admin.site.register(Tr, TrAdmin)


class TzAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_systemic', )
    ordering = ('name',)


admin.site.register(Tz, TzAdmin)


class RelationAdmin(admin.ModelAdmin):
    list_display = ('bz', 'tr', 'rz', 'author', 'date', 'user' )
    save_as = True
    autocomplete_fields = ['bz', 'rz', 'author']
    search_fields = ['bz__name', 'rz__name']
    ordering = ('-date',)

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        super().save_model(request, obj, form, change)

    class Media:
        css = {
            "all": ("drevo/css/style.css",)
        }


admin.site.register(Relation, RelationAdmin)


class GlossaryTermAdmin(admin.ModelAdmin):
    list_display = ('name', 'description' )
    ordering = ('name',)

    def get_form(self, request, obj=None, **kwargs):
        kwargs['form'] = GlossaryTermForm
        return super().get_form(request, obj, **kwargs)    


admin.site.register(GlossaryTerm, GlossaryTermAdmin)