from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from users.models import User, Profile


class ProfileInlined(admin.StackedInline):
    model = Profile
    can_delete = False
    

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInlined, )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )

    fieldsets = (
        (
            None,
            {
                'fields': ('username', 'password')
            }
        ),
        (
            'Персональные данные',
            {
                'fields': ('first_name',
                           'last_name',
                           'email')
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
