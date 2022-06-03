from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from users.models import User, Profile, Favourite


class FavouritesInlined(admin.StackedInline):
    model = Favourite
    can_delete = False
    filter_horizontal = ('favourites', )


class ProfileInlined(admin.StackedInline):
    model = Profile
    can_delete = False


class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInlined, FavouritesInlined)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        })
    )


admin.site.register(User, UserAdmin)
