from django.contrib import admin
from users.models import User, Profile, Favourites

admin.site.register(User)
admin.site.register(Profile)
admin.site.register(Favourites)
