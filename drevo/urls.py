from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import (DrevoListView,
                    DrevoView,
                    ZnanieDetailView,
                    ZnanieByLabelView,
                    AuthorDetailView,
                    AuthorsListView,
                    LabelsListView,
                    GlossaryListView,
                    ZnanieRatingView,
                    CommentPageView,
                    CommentSendView,
                    KnowledgeSearchView,
                    AuthorSearchView,
                    TagSearchView)

urlpatterns = [
    path('category/<int:pk>', DrevoListView.as_view(), name='drevo_type'),
    path('', DrevoView.as_view(), name='drevo'),
    path('znanie/<int:pk>', ZnanieDetailView.as_view(), name='zdetail'),
    path('znanie/<int:pk>/comments/', CommentPageView.as_view()),
    path('znanie/<int:pk>/comments/send/', CommentSendView.as_view()),
    path('znanie/<int:pk>/vote/<str:vote>/',
         ZnanieRatingView.as_view(), name='znrating'),
    path('label/<int:pk>', ZnanieByLabelView.as_view(), name='zlabel'),
    path('author/<int:pk>', AuthorDetailView.as_view(), name='author'),
    path('authors/', AuthorsListView.as_view(), name='authors'),
    path('labels/', LabelsListView.as_view(), name='labels'),
    path('glossary/', GlossaryListView.as_view(), name='glossary'),
    path('search/knowledge',
         KnowledgeSearchView.as_view(),
         name='search_knowledge'),
    path('search/author',
         AuthorSearchView.as_view(),
         name='search_author'),
    path('search/tag',
         TagSearchView.as_view(),
         name='search_tag'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
