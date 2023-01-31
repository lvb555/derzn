from django.urls import path
from .views import help_view

urlpatterns = [
    path('', help_view, name="help_page"),
    path('<path:tag>', help_view, name="help_page"),
]
