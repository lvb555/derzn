from django.contrib import admin
from drevo.models import Znanie, Tz, Author, Label, Tr, Relation, Category
from mptt.admin import DraggableMPTTAdmin
from .forms import ZnanieForm

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


class ZnanieAdmin(admin.ModelAdmin):
    list_display = ('name', 'tz', 'href', 'author', 'date', 'user')
    ordering = ('order',)
    save_as = True
    autocomplete_fields = ['labels', 'category']
    search_fields = ['name']

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        super().save_model(request, obj, form, change)

    def get_form(self, request, obj=None, **kwargs):
        kwargs['form'] = ZnanieForm
        return super().get_form(request, obj, **kwargs)

    class Media:
        css = {
            "all": ("drevo/css/style.css",)
        }

admin.site.register(Znanie, ZnanieAdmin)


class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name', )
    ordering = ('name',)

    class Media:
        css = {
            "all": ("drevo/css/style.css",)
        }

admin.site.register(Author, AuthorAdmin)


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
    autocomplete_fields = ['bz', 'rz']
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
