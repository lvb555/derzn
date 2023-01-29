from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from drevo.views.interviews_view import interview_view
from drevo.views.my_interview_view import my_interview_view
from .views import (
    DrevoListView,
    DrevoView,
    KnowledgeView,
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
    FavouritesView,
    FavouriteProcessView,
    QuestionExpertWorkPage,
    friends_view,
    friends_added_view,
    KnowledgeFormView,
    QuizListView,
    QuizResultAdd,
    KnowledgeStatisticFormView,
    GroupKnowledgeView,
    QuizDetailView,
    InfographicsView,
    GroupInfographicsView,
    my_knowledge_grade,
    GroupKnowledgeStatisticsView,
    parameter_settings,
)
from .views import send_znanie, knowledge_feed_view
from .views.expert_work.proposal_delete_view import ProposalDeleteView
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
    NotifyExpertsView,
)
from .views.public_people import public_people_view, public_human
from .views.quiz_result import show_quiz_result
from .views.subscribe_to_author_view import sub_by_author
from .views.subscription_by_tag_view import sub_by_tag
from drevo.views.developer_view import developer_view
from .views.knowledge_tp_view import (
    KnowledgeCreateView,
    UserKnowledgeProcessView,
    KnowledgeUpdateView,
    KnowledgeChangeStatus,
    ExpertKnowledgeProcess,
    RedactorKnowledgeProcess,
    DirectorKnowledgeProcess,
    KlzKnowledgeProcess,
)

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
    path('znanie/<int:pk>/grade/statistic', KnowledgeStatisticFormView.as_view(), name='grade_statistic'),
    path('znanie/<int:pk>/grade/group', GroupKnowledgeView.as_view(), name="group_knowledge"),
    path('znanie/<int:pk>/grade/group/infographics', GroupInfographicsView.as_view(), name="grade_group_infographics"),
    path('znanie/<int:pk>/grade/group/statistics', GroupKnowledgeStatisticsView.as_view(), name="grade_group_statistics"),
    path("znanie/<int:pk>/grade/infographics", InfographicsView.as_view(), name="grade_infographics"),
    path("my_knowledge_grade/", my_knowledge_grade, name="my_knowledge_grade"),
    path("all_quizzes/", QuizListView.as_view(), name="all_quizzes"),
    path("quiz/<int:pk>", QuizDetailView.as_view(), name="quiz"),
    path("quiz/<int:pk>/quiz_result/", QuizResultAdd.as_view()),
    path("quiz_results/<int:id>", show_quiz_result, name="show_quiz_result"),
    path("public_people", public_people_view, name="public_people"),
    path("public_people/<int:id>", public_human, name="public_human"),
    path("label/<int:pk>", ZnanieByLabelView.as_view(), name="zlabel"),
    path("author/<int:pk>", AuthorDetailView.as_view(), name="author"),
    path("authors/", AuthorsListView.as_view(), name="authors"),
    path("labels/", LabelsListView.as_view(), name="labels"),
    path("glossary/", GlossaryListView.as_view(), name="glossary"),
    path("knowledge/", KnowledgeView.as_view(), name="knowledge"),
    path("search/knowledge", KnowledgeSearchView.as_view(), name="search_knowledge"),
    path("new_knowledge/", NewKnowledgeListView.as_view(), name="new_knowledge"),
    path("search/author", AuthorSearchView.as_view(), name="search_author"),
    path("search/tag", TagSearchView.as_view(), name="search_tag"),
    path("history/", BrowsingHistoryListView.as_view(), name="history"),
    path("subscribe_to_author/<int:id>", sub_by_author, name="subscribe_to_author"),
    path("subscription_by_tag/<int:id>", sub_by_tag, name="subscription_by_tag"),
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
    path(
        "interview/<int:interview_pk>/questions/<int:question_pk>/<int:pk>",
        ProposalDeleteView.as_view(),
        name="delete",
    ),
    path("admin/interview/", AllInterviewView.as_view(), name="all_interview"),
    path(
        "admin/interview/<int:pk>/questions/",
        InterviewQuestionsView.as_view(),
        name="interview_quests",
    ),
    path(
        "admin/interview/<int:inter_pk>/questions/<int:quest_pk>/",
        question_admin_work_view,
        name="question_admin_work",
    ),
    path(
        "admin/interview/<int:inter_pk>/questions/<int:quest_pk>/knowledge_edit/<int:znanie_pk>/",
        AdminEditingKnowledgeView.as_view(),
        name='admin_knowledge_edit'
    ),
    path(
        "admin/interview/<int:inter_pk>/questions/<int:quest_pk>/notify_experts/",
        NotifyExpertsView.as_view(),
        name='admin_notify_experts'
    ),

    path("friends/", friends_view, name="friends"),
    path("friends/friends_added/", friends_added_view, name="friends_added"),
    # path("friends/friends_invite/", friends_invite_view, name="friends_invite"),
    path(
        "knowledge-feed/",
        knowledge_feed_view.knowledge_feed_view,
        name="knowledge_feed",
    ),
    path(
        "knowledge-feed/delete/<int:message_id>/",
        knowledge_feed_view.delete_message,
        name="delete_message",
    ),
    path("developer/", developer_view, name="developer_page"),
    path("znanie_create/", KnowledgeCreateView.as_view(), name="znanie_create"),
    path(
        "znanie_user_tp/",
        UserKnowledgeProcessView.as_view(),
        name="znanie_user_process",
    ),
    path("znanie_update/<pk>/", KnowledgeUpdateView.as_view(), name="znanie_update"),
    path(
        "znanie_status/<pk>/<status>",
        KnowledgeChangeStatus.as_view(),
        name="znanie_change_status",
    ),
    path(
        "znanie_expert_tp/",
        ExpertKnowledgeProcess.as_view(),
        name="znanie_expert_process",
    ),
    path(
        "znanie_redactor_tp/",
        RedactorKnowledgeProcess.as_view(),
        name="znanie_redactor_process",
    ),
    path(
        "znanie_director_tp/",
        DirectorKnowledgeProcess.as_view(),
        name="znanie_director_process",
    ),
    path("klz/", KlzKnowledgeProcess.as_view(), name="klz"),
    path('profile/settings/', parameter_settings, name='parameter_settings')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
