from django.contrib import admin
from django import forms
from ckeditor.widgets import CKEditorWidget
from .models import HelpPage


class HelpAdminForm(forms.ModelForm):

    content = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = HelpPage
        fields = ["header", "content", "url_tag"]


class HelpPageAdmin(admin.ModelAdmin):
    form = HelpAdminForm
    list_display = ("pk", "header", "url_tag")
    search_fields = ("header",)
    empty_value_display = "-пусто-"


admin.site.register(HelpPage, HelpPageAdmin)
