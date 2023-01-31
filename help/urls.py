from django.urls import path
from .views import help_view

urlpatterns = [
    path('', help_view, name="help"),
    path('<int:pk>', help_view, name="help"),
]
