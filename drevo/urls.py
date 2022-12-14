from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from drevo.views.interviews_view import interview_view
from drevo.views.my_interview_view import my_interview_view
from .views import (
    DrevoListView,
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
    NewKnowledgeListView,
    BrowsingHistoryListView,
    SubscribeToAuthor,
    FavouritesView,
    FavouriteProcessView,
    QuestionExpertWorkPage,
    friends_view,
    friends_added_view,
    friends_invite_view,
    KnowledgeFormView,
)
from .views import send_znanie, knowledge_feed_view, send_to_feed_view
from .views.expert_work.views import (
    propose_answer,
    update_answer_proposal,
    update_proposed_answer,
)
from .views.admin_interview_work.views import (
    AllInterviewView,
    InterviewQuestionsView,
    question_admin_work_view,
    AdminEditingKnowledgeView,
)
from .views.subscription_by_tag_view import sub_by_tag

urlpatterns = [
    path("category/<int:pk>", DrevoListView.as_view(), name="drevo_type"),
    path("", DrevoView.as_view(), name="drevo"),
    path("znanie/<int:pk>", ZnanieDetailView.as_view(), name="zdetail"),
    path("znanie/<int:pk>/favourite", FavouriteProcessView.as_view()),
    path("znanie/<int:pk>/comments/", CommentPageView.as_view()),
    path("znanie/<int:pk>/comments/send/", CommentSendView.as_view()),
    path(
        "znanie/<int:pk>/vote/<str:vote>/", ZnanieRatingView.as_view(), name="znrating"
    ),
    path("znanie/<int:pk>/message/send/", send_znanie, name="zsend_mes"),
    path("znanie/<int:pk>/grade/", KnowledgeFormView.as_view(), name="grade"),
    path("label/<int:pk>", ZnanieByLabelView.as_view(), name="zlabel"),
    path("author/<int:pk>", AuthorDetailView.as_view(), name="author"),
    path("authors/", AuthorsListView.as_view(), name="authors"),
    path("labels/", LabelsListView.as_view(), name="labels"),
    path("glossary/", GlossaryListView.as_view(), name="glossary"),
    path("search/knowledge", KnowledgeSearchView.as_view(), name="search_knowledge"),
    path("new_knowledge/", NewKnowledgeListView.as_view(), name="new_knowledge"),
    path("search/author", AuthorSearchView.as_view(), name="search_author"),
    path("search/tag", TagSearchView.as_view(), name="search_tag"),
    path("history/", BrowsingHistoryListView.as_view(), name="history"),
    path(
        "subscribe_to_author/", SubscribeToAuthor.as_view(), name="subscribe_to_author"
    ),
    path('subscription_by_tag/', sub_by_tag,
         name='subscription_by_tag'),
    path("favourites/", FavouritesView.as_view(), name="favourites"),
    path("my_interview/", my_interview_view, name="my_interview"),
    path("interview/<int:pk>/", interview_view, name="interview"),
    path(
        "interview/<int:interview_pk>/questions/<int:question_pk>/expertise",
        QuestionExpertWorkPage.as_view(),
        name="question_expert_work",
    ),
    path(
        "interview/<int:interview_pk>/questions/<int:question_pk>/answers/<int:answer_pk>",
        update_answer_proposal,
        name="update_answer_proposal",
    ),
    path(
        "interview/<int:interview_pk>/questions/<int:question_pk>/new_answers",
        propose_answer,
        name="propose_answer",
    ),
    path(
        "interview/new_answers/<int:proposal_pk>",
        update_proposed_answer,
        name="update_proposed_answer",
    ),
    path("admin/interview/", AllInterviewView.as_view(), name='all_interview'),
    path("admin/interview/<int:pk>/questions/", InterviewQuestionsView.as_view(), name='interview_quests'),
    path("admin/interview/<int:inter_pk>/questions/<int:quest_pk>/", question_admin_work_view,
         name='question_admin_work'),
    path(
        "admin/interview/<int:inter_pk>/questions/<int:quest_pk>/knowledge_edit/<int:znanie_pk>/",
        AdminEditingKnowledgeView.as_view(),
        name='admin_knowledge_edit'
    ),

    path("friends/", friends_view, name="friends"),
    path("friends/friends_added/", friends_added_view, name="friends_added"),
    path("friends/friends_invite/", friends_invite_view, name="friends_invite"),

    path('knowledge-feed/', knowledge_feed_view.knowledge_feed_view, name='knowledge_feed'),
    path('knowledge-feed/delete/<int:message_id>/', knowledge_feed_view.delete_message, name='delete_message'),
    path('knowledge-feed/send/<int:znanie_id>/', send_to_feed_view.send_to_feed_view, name='send_to_feed'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
