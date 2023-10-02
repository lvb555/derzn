from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from users.models import User, Profile, MenuSections, UserSuggection, SuggestionType


class ProfileInlined(admin.StackedInline):
    model = Profile
    can_delete = False
    

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInlined, )
    readonly_fields=('user_friends',)

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )
    autocomplete_fields = ["sections", ]
    fieldsets = (
        (
            None,
            {
                'fields': ('username', 'password', 'user_friends')
            }
        ),
        (
            'Персональные данные',
            {
                'fields': ('first_name',
                           'last_name',
                           'email',
                           'is_public',
                           'cookie_acceptance',
                           'sections',
                           'job')
            }
        ),
        (
            'Разрешения',
            {
                'fields': ('is_active',
                           'is_staff',
                           'is_superuser',
                           'is_expert',
                           'is_redactor',
                           'is_director',
                           'in_klz',
                           'groups',
                           'user_permissions'),
            }
        )
    )
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_first_name', 'user_last_name', 'user_email', 'gender', 'birthday_at')
    list_editable = ('gender', 'birthday_at')

    def user_first_name(self, obj):
        return obj.user.first_name
    user_first_name.short_description = 'Имя'

    def user_last_name(self, obj):
        return obj.user.last_name
    user_last_name.short_description = 'Фамилия'

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = "Email"

@admin.register(MenuSections)
class MenuSectionsAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ["name"]

@admin.register(UserSuggection)
class UserSuggestionAdmin(admin.ModelAdmin):
    list_display = ('parent_knowlege', 'name', 'user', 'expert', 'is_approve', 'suggestions_type')
    list_filter = ('suggestions_type', 'user', 'parent_knowlege')

@admin.register(SuggestionType)
class SuggestionTypeAdmin(admin.ModelAdmin):
    list_display = ('type_name', 'weight')
    list_filter = ('type_name', 'weight')