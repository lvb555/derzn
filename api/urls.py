from django.urls import path

from api.knowledge_relations_view import KnowledgeRelationsAPIView
from api.views import CategoryChildrenAPIView

urlpatterns = [
    path('categories/', CategoryChildrenAPIView.as_view(), name='category-root'),
    path('categories/<pk>/children/', CategoryChildrenAPIView.as_view(), name='category-children'),
    path('categories/uncategorized/children', CategoryChildrenAPIView.as_view(),
         kwargs={'pk': 'uncategorized'}, name='uncategorized-knowledge'),
    path('knowledge/<int:id>/relations/', KnowledgeRelationsAPIView.as_view(), name='knowledge-relations'),
]