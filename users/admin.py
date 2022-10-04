from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from users.models import User, Profile


class ProfileInlined(admin.StackedInline):
    model = Profile
    can_delete = False


class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInlined, )

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        })
    )


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


admin.site.register(User, UserAdmin)
admin.site.register(Profile, ProfileAdmin)
