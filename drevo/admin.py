from django.contrib import admin
from drevo.models import Znanie, Tz, Author, Label, Tr, Relation, Category
from mptt.admin import DraggableMPTTAdmin

admin.site.register(
    Category,
    DraggableMPTTAdmin,
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

admin.site.register(Label, LabelAdmin)


class ZnanieAdmin(admin.ModelAdmin):
    list_display = ('name', 'tz', 'href', 'author', 'date')
    ordering = ('name',)

admin.site.register(Znanie, ZnanieAdmin)


class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name', )
    ordering = ('name',)

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
    ordering = ('-date',)

admin.site.register(Relation, RelationAdmin)