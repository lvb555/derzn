from django.urls import path
from api.views import CategoryChildrenAPIView

urlpatterns = [
    path('categories/', CategoryChildrenAPIView.as_view(), name='category-root'),
    path('categories/<pk>/children/', CategoryChildrenAPIView.as_view(), name='category-children'),
    path('categories/uncategorized/children', CategoryChildrenAPIView.as_view(), kwargs={'pk': 'uncategorized'}, name='uncategorized-knowledge'),
]