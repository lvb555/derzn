from django.contrib import admin
from django import forms
from ckeditor.widgets import CKEditorWidget
from django.utils.safestring import mark_safe

from .models import Help, HelpURLTag
from mptt.admin import DraggableMPTTAdmin
from django.utils.html import format_html


@admin.register(HelpURLTag)
class HelpURLTagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name',)
    list_display_links = ('pk', 'name',)
    search_fields = ('name',)
    save_as = True


class HelpAdminForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorWidget(), required=False)

    class Meta:
        model = Help
        fields = ('name', 'content', 'parent', 'url_tag', 'is_published', 'is_group',)


@admin.register(Help)
class HelpAdmin(DraggableMPTTAdmin):
    form = HelpAdminForm
    search_fields = ('name',)
    list_display = (
        'tree_actions',
        'indented_title_ispublished',
        'get_safe_content',
    )
    list_display_links = ("indented_title_ispublished",)
    empty_value_display = '-пусто-'

    def indented_title_ispublished(self, instance):
        published_str = "published" if instance.is_published else "unpublished"
        return format_html(
            '<div style="text-indent:{}px" class="{}">{}</div>',
            instance._mpttfield("level") * self.mptt_level_indent,
            published_str,
            instance.name,
        )
    indented_title_ispublished.short_description = "Категория помощи"

    def get_safe_content(self, instance):
        return mark_safe(instance.content)

    get_safe_content.short_description = 'Содержание'

    class Media:
        css = {"all": ("drevo/css/style.css",)}
