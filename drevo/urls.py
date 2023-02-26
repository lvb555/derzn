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
    FavouritesView,
    FavouriteProcessView,
    QuestionExpertWorkPage,
    friends_view,
    friends_added_view,
    get_rows_and_columns,
    filling_tables,
    znanie_attributes,
    show_new_znanie,
    show_filling_tables_page,
    KnowledgeFormView,
    QuizListView,
    QuizResultAdd,
    KnowledgeStatisticFormView,
    GroupKnowledgeView,
    QuizDetailView,
    InfographicsView,
    GroupInfographicsView,
    my_knowledge_grade,
    knowledges_grades,
    GroupKnowledgeStatisticsView,
    parameter_settings,
    send_message_view,
    messages_feed_view,
)
from .views import send_znanie, knowledge_feed_view
from .views.browsing_history import browsing_history


from .views.expert_work.views import (
    propose_answer,
    sub_answer_create_view,
    ExpertProposalDeleteView,
    set_answer_as_incorrect,
    set_answer_is_agreed,
    proposal_update_view,
)
from .views.admin_interview_work.views import (
    AllInterviewView,
    InterviewQuestionsView,
    question_admin_work_view,
    AdminEditingKnowledgeView,
    NotifyExpertsView,
)
from .views.interview_and_proposal import my_interview, my_proposal
from .views.klz_all_knowledges import klz_all
from .views.my_favourites import my_favourites
from .views.my_knowledge import my_knowledge, my_preknowledge, my_expertise
from .views.new_knowledges import new_knowledge
from .views.public_people import public_people_view, public_human
from .views.quiz_result import show_quiz_result
from .views.subscribe_to_author_view import sub_by_author
from .views.subscription_by_category_view import sub_by_category
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
    path("knowledges_grades/", knowledges_grades, name="knowledges_grades"),
    path("my_knowledge_grade/<int:id>/", my_knowledge_grade, name="my_knowledge_grade"),
    path("row/", get_rows_and_columns, name="get_rows_and_columns"),
    path("column/", znanie_attributes, name="znanie_attributes"),
    path("filling_tables/", filling_tables, name="filling_tables"),
    path("show_new_znanie/", show_new_znanie, name="show_new_znanie"),
    path("show_filling_tables_page/", show_filling_tables_page, name="show_filling_tables_page"),
    path("all_quizzes/", QuizListView.as_view(), name="all_quizzes"),
    path("quiz/<int:pk>", QuizDetailView.as_view(), name="quiz"),
    path("quiz/<int:pk>/quiz_result/", QuizResultAdd.as_view()),
    path("quiz_results/<int:id>/", show_quiz_result, name="show_quiz_result"),
    path("public_people", public_people_view, name="public_people"),
    path("public_people/<int:id>/", public_human, name="public_human"),
    path("klz_/", klz_all, name="clz"),
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
    path("history/<int:id>/", browsing_history, name="history"),
    path("subscribe_to_author/<int:id>/", sub_by_author, name="subscribe_to_author"),
    path("subscription_by_tag/<int:id>/", sub_by_tag, name="subscription_by_tag"),
    path("subscription_by_category/<int:id>/", sub_by_category, name="subscription_by_category"),
    path("new_knowledges/<int:id>/", new_knowledge, name="new_knowledges"),
    path("favourites/", FavouritesView.as_view(), name="favourites"),
    path("my_favourites/<int:id>/", my_favourites, name="my_favourites"),
    path("my_knowledge/<int:id>/", my_knowledge, name="my_knowledge"),
    path("my_preknowledge/<int:id>/", my_preknowledge, name="my_preknowledge"),
    path("my_expertise/<int:id>/", my_expertise, name="my_expertise"),
    path("my__interview/<int:id>/", my_interview, name="my_interview_profile"),
    path("my_proposal/<int:id>/", my_proposal, name="my_proposal"),
    path("my_interview/", my_interview_view, name="my_interview"),
    path("interview/<int:pk>/", interview_view, name="interview"),
    path(
        "interview/<int:interview_pk>/questions/<int:question_pk>/expertise",
        QuestionExpertWorkPage.as_view(),
        name="question_expert_work",
    ),
    path(
        "interview/<int:interview_pk>/questions/<int:question_pk>/new_answers",
        propose_answer,
        name="propose_answer",
    ),
    path(
        "interview/delete_proposal",
        ExpertProposalDeleteView.as_view(),
        name="delete_proposal",
    ),
    path(
        'interview/questions/<int:quest_pk>/answer/<int:answer_pk>/add_subanswer',
        sub_answer_create_view,
        name='add_subanswer'
    ),
    path(
        'interview/answer/<int:proposal_pk>/answer_as_incorrect',
        set_answer_as_incorrect,
        name='set_answer_as_incorrect'
    ),
    path(
        'interview/answer/<int:proposal_pk>/answer_is_agreed',
        set_answer_is_agreed,
        name='set_answer_is_agreed'
    ),
    path(
        'interview/proposal/<int:proposal_pk>/update',
        proposal_update_view,
        name='proposal_update'
    ),
    path("admin/interview/", AllInterviewView.as_view(), name="all_interview"),
    path(
        "admin/interview/<int:pk>/questions/",
        InterviewQuestionsView.as_view(),
        name="interview_quests",
    ),
    path(
        "admin/interview/<int:inter_pk>/questions/<int:quest_pk>/proposals/",
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
        name="delete_feed_message",
    ),
    path("send-message/", send_message_view.send_message, name = "send_message"),
    path("messages-feed/", messages_feed_view.messages_feed, name = "messages_feed"),
    path(
        "messages-feed/delete/<int:message_id>/",
        send_message_view.delete_message,
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
