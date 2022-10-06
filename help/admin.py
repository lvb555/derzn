from django.contrib import admin

from .models import HelpPage


class HelpPageAdmin(admin.ModelAdmin):
    list_display = ("pk", "header", "content", "tag")
    search_fields = ("header",)
    empty_value_display = "-пусто-"


admin.site.register(HelpPage, HelpPageAdmin)
