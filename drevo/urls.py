from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from drevo.views.interviews_view import interview_view
from drevo.views.my_interview_view import my_interview_view
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
                    TagSearchView,
                    KnowledgeFormView,
                    NewKnowledgeListView,
                    BrowsingHistoryListView,
                    SubscribeToAuthor,
                    FavouritesView,
                    FavouriteProcessView)

urlpatterns = [
    path('category/<int:pk>', DrevoListView.as_view(), name='drevo_type'),
    path('', DrevoView.as_view(), name='drevo'),
    path('znanie/<int:pk>', ZnanieDetailView.as_view(), name='zdetail'),
    path('znanie/<int:pk>/favourite', FavouriteProcessView.as_view()),
    path('znanie/<int:pk>/comments/', CommentPageView.as_view()),
    path('znanie/<int:pk>/comments/send/', CommentSendView.as_view()),
    path('znanie/<int:pk>/vote/<str:vote>/',
         ZnanieRatingView.as_view(), name='znrating'),
    path('znanie/<int:pk>/grade/', KnowledgeFormView.as_view(), name='grade'),
    path('label/<int:pk>', ZnanieByLabelView.as_view(), name='zlabel'),
    path('author/<int:pk>', AuthorDetailView.as_view(), name='author'),
    path('authors/', AuthorsListView.as_view(), name='authors'),
    path('labels/', LabelsListView.as_view(), name='labels'),
    path('glossary/', GlossaryListView.as_view(), name='glossary'),
    path('search/knowledge',
         KnowledgeSearchView.as_view(),
         name='search_knowledge'),
    path('new_knowledge/', NewKnowledgeListView.as_view(),
         name='new_knowledge'),
    path('search/author',
         AuthorSearchView.as_view(),
         name='search_author'),
    path('search/tag',
         TagSearchView.as_view(),
         name='search_tag'),
    path('history/',
         BrowsingHistoryListView.as_view(),
         name='history'),
    path('subscribe_to_author/', SubscribeToAuthor.as_view(),
         name='subscribe_to_author'),
    path('favourites/',
         FavouritesView.as_view(),
         name='favourites'),
    path('my_interview/', my_interview_view, name='my_interview'),
    path('interview/<int:pk>/', interview_view, name='interview'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
