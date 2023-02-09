from django.urls import path
from custom_admin.views import get_dump

urlpatterns = [
    path('get-dump/', get_dump, name='get-dump')
]
