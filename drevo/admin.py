from django.contrib import admin
from drevo.models import Znanie, Tz, Author, Label, Tr, Relation, Category, ZnImage, AuthorType
from mptt.admin import DraggableMPTTAdmin
from .forms import ZnanieForm, AuthorForm
from django.utils.safestring import mark_safe


class CategoryMPTT(DraggableMPTTAdmin):
    search_fields = ['name']

    class Media:
        css = {
            "all": ("drevo/css/style.css",)
        }


admin.site.register(
    Category,
    CategoryMPTT,
    list_display=(
        'tree_actions',
        'indented_title',
    ),
    list_display_links=(
        'indented_title',
    ),
)


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
    list_display = ('name', 'tz', 'href2link', 'author', 'updated_at', 'user')
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

    class Media:
        css = {
            "all": ("drevo/css/style.css",)
        }


admin.site.register(Znanie, ZnanieAdmin)


class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', )
    ordering = ('name',)
    search_fields = ['name']
    list_filter = ('type', )

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
    list_display = ('name', )
    ordering = ('name',)


admin.site.register(Tr, TrAdmin)


class TzAdmin(admin.ModelAdmin):
    list_display = ('name', )
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
