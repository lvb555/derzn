from django.contrib import admin
from django import forms
from ckeditor.widgets import CKEditorWidget
from .models import HelpPage, CategoryHelp
from mptt.admin import DraggableMPTTAdmin
from django.utils.html import format_html


class HelpAdminForm(forms.ModelForm):

    content = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = HelpPage
        fields = ["header", "content", "category"]


class HelpPageAdmin(admin.ModelAdmin):
    form = HelpAdminForm
    list_display = ("pk", "header", "category")
    search_fields = ("header",)
    empty_value_display = "-пусто-"


class HelpCategoryAdmin(DraggableMPTTAdmin):
    search_fields = ["name"]
    list_display = (
        "tree_actions",
        "indented_title_ispublished",
        "description",
        "url_tag",
    )
    list_display_links = ("indented_title_ispublished",)
    empty_value_display = "-пусто-"

    def indented_title_ispublished(self, instance):
        published_str = "published" if instance.is_published else "unpublished"
        return format_html(
            '<div style="text-indent:{}px" class="{}">{}</div>',
            instance._mpttfield("level") * self.mptt_level_indent,
            published_str,
            instance.name,  # Or whatever you want to put here
        )
    indented_title_ispublished.short_description = "Категория помощи"

    class Media:
        css = {"all": ("drevo/css/style.css",)}


admin.site.register(HelpPage, HelpPageAdmin)
admin.site.register(CategoryHelp, HelpCategoryAdmin)
