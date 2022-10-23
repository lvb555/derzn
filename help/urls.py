from django.urls import path
# from .views import CategoryListView

from . import views

urlpatterns = [
    path("", views.help, name="help"),
    path("<str:category>", views.help, name="help"),
]
