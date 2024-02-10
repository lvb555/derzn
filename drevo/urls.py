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
    AlgorithmDetailView,
    AlgorithmListView,
    AlgorithmResultAdd,
    EditAlgorithm,
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
    about_proj,
    friends_view,
    friends_added_view,
    ZnaniyaForConstructorView,
    MainZnInConstructorCreateView,
    FillingTablesView,
    save_zn_to_cell_in_table_from_request,
    get_cell_for_table,
    relation_in_table_create_update_view,
    element_of_group_in_table_create_update_view,
    delete_table,
    delete_row_or_column,
    row_and_column_existence,
    show_filling_tables_page,
    delete_element_of_relation,
    KnowledgeFormView,
    QuizListView,
    QuizResultAdd,
    KnowledgeStatisticFormView,
    GroupKnowledgeView,
    QuizDetailView,
    QuizConstructorView,
    question_create_update_in_quiz,
    answer_create_update_in_quiz,
    answers_in_quiz_existence,
    delete_answers_or_questions_to_quiz,
    delete_quiz,
    get_answers_to_selected_question_of_quiz,
    InfographicsView,
    GroupInfographicsView,
    my_knowledge_grade,
    knowledges_grades,
    GroupKnowledgeStatisticsView,
    ParameterSettingsView,
    update_user_settings,
    send_message_view,
    messages_feed_view,
    KnowledgeTypesView,
    RelationTypesView,
    SpecialPermissionsDeleteView,
    ExpertsPermissionsDeleteView,
    delete_competence_expert,
    ExpertKnowledgeView,
    delete_editor_permissions,
    AdminsPermissionsDeleteView,
    delete_competence_admin,
    get_required_tr,
    get_required_rz,
    search_by_tree_view,
    advance_search_by_tree_view,
    PreparingRelationsCreateView,
    PreparingRelationsUpdateView,
    PreparingRelationsExpertiseView,
    PreparingRelationsPublicationView,
    RelationCreatePageView,
    DocumentTextTemplateEdit,
    DocumentTextTemplateCreate,
    turple_processing_view,
    document_object_processing_view,
    check_related,
    relation_create_view,
    relation_delete_view,
    create_additional_knowledge,
    get_related_tz,
    additional_knowledge_update_view,
    RelationUpdatePageView,
    relation_update_view,
    RelationsExpertisePageView,
    relation_expertise_view,
    RelationsPublicationPageView,
    relation_publication_view,
    get_tr_for_create_relation_in_tree_constructor,
    get_rel_zn_in_tree_constructor_from_request,
    TreeConstructorView,
    TableConstructorView,
    save_rel_in_tree_constructor,
    make_copy_of_algorithm,
    delete_relation_in_tree_constructor,
    get_tr_for_edit_relation_in_tree_constructor,
    edit_znanie_in_tree_constructor,
    create_zn_in_tree_constructor,
    is_current_user_creator_of_zn,
    delete_complex_zn,
    create_zn_for_cell,
    check_algorithm_correctness_from_request,
    edit_main_zn_in_constructor,
    get_order_of_relation,
    delete_algorithm,
    delete_zn_in_cell_in_table,

)

from .views import send_znanie, knowledge_feed_view
from .views.appeal_in_support import appeal
from .views.browsing_history import browsing_history
from .views.cookie_acceptance_process_view import CookieAcceptance
from .views.user_suggestion_view import UserSuggestionView
from .views.users_documents import CreateDocumentView, \
    ChangeDocumentView, DeleteDocumentView

from .views.expert_work.views import (
    propose_answer,
    sub_answer_create_view,
    ExpertProposalDeleteView,
    set_answer_as_incorrect,
    set_answer_is_agreed,
    proposal_update_view,
    set_new_answer_is_agreed,
)
from .views.admin_interview_work.views import (
    AllInterviewView,
    InterviewQuestionsView,
    question_admin_work_view,
    AdminEditingKnowledgeView,
    NotifyExpertsView,
)
from .views.popular_knowledges import get_popular_knowledges
from .views.privacy_policy import PrivacyPolicyView
from .views.special_permissions_for_public import get_special_permission
from .views.special_permissions_work.view import (
    SpecialPermissionsView,
    set_users_as_editor,
    ExpertsCandidatesListView,
    set_users_as_expert,
    AdminsCandidatesListView,
    set_users_as_admin,
    UsersSpecialPermissionsView,
    ExpertCandidateKnowledgeView,
    AdminCandidateKnowledgeView,
)
from .views.questions import save_answer, questions_and_check_answers
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
    path("cookie_acceptance/", CookieAcceptance.as_view()),
    path("", DrevoView.as_view(), name="drevo"),
    path("znanie/<int:pk>", ZnanieDetailView.as_view(), name="zdetail"),
    path("znanie/<int:pk>/suggestions", UserSuggestionView.as_view(), name="create-suggestion"),
    path("znanie/<int:pk>/questions_user", save_answer, name="questions_user"),
    path("znanie/<int:pk>/questions_and_check_answers", questions_and_check_answers, name="questions_and_check_answers"),
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
    path('znanie/<int:doc_pk>/document-template/edit-text/<int:text_pk>', DocumentTextTemplateEdit.as_view(), name='edit_text_template'),
    path('znanie/<int:doc_pk>/document-template/create-text/', DocumentTextTemplateCreate.as_view(), name='create_text_template'),
    path('znanie/<int:doc_pk>/document-template/turple_processing', turple_processing_view),
    path('znanie/<int:doc_pk>/document-template/document_object_processing', document_object_processing_view),
    path("knowledges_grades/", knowledges_grades, name="knowledges_grades"),
    path("my_knowledge_grade/<int:id>/", my_knowledge_grade, name="my_knowledge_grade"),
    path("about/", about_proj.AboutView.as_view(), name="about_proj"),
    path('appeal/', appeal, name='appeal'),
    path("all_quizzes/", QuizListView.as_view(), name="all_quizzes"),
    path("quiz/<int:pk>", QuizDetailView.as_view(), name="quiz"),
    path("quiz/<int:pk>/quiz_result/", QuizResultAdd.as_view()),
    path("quiz/<int:pk>/vote/<str:vote>", ZnanieRatingView.as_view()),
    path('quiz/<int:pk>/favourite', FavouriteProcessView.as_view()),
    path("quiz_results/<int:id>/", show_quiz_result, name="show_quiz_result"),
    path("question_create_update_in_quiz/", question_create_update_in_quiz,
         name="question_create_update_in_quiz"),
    path("answer_create_update_in_quiz/", answer_create_update_in_quiz,
         name="answer_create_update_in_quiz"),
    path("delete_quiz/", delete_quiz, name="delete_quiz"),
    path("answers_in_quiz_existence/", answers_in_quiz_existence, name="answers_in_quiz_existence"),
    path("public_people", public_people_view, name="public_people"),
    path("public_people/<int:id>/", public_human, name="public_human"),
    path("klz_/", klz_all, name="clz"),
    path("label/<int:pk>", ZnanieByLabelView.as_view(), name="zlabel"),
    path("author/<int:pk>", AuthorDetailView.as_view(), name="author"),
    path("authors/", AuthorsListView.as_view(), name="authors"),
    path("labels/", LabelsListView.as_view(), name="labels"),
    path("glossary/", GlossaryListView.as_view(), name="glossary"),
    path("knowledge/", KnowledgeView.as_view(), name="knowledge"),
    path('knowledge/types/<int:type_pk>', KnowledgeTypesView.as_view(), name='knowledge_type'),
    path('relations/types/<int:type_pk>', RelationTypesView.as_view(), name='relation_type'),
    path("all_algorithms/", AlgorithmListView.as_view(), name="all_algorithms"),
    path("algorithm/<int:pk>", AlgorithmDetailView.as_view(), name="algorithm"),
    path("algorithm/<int:pk>/algorithm_result/", AlgorithmResultAdd.as_view()),
    path("algorithm/<int:pk>/edit_algorithm/", EditAlgorithm.as_view()),
    path("search/knowledge", KnowledgeSearchView.as_view(), name="search_knowledge"),
    path("new_knowledge/", NewKnowledgeListView.as_view(), name="new_knowledge"),
    path("create_document/<int:pk>", CreateDocumentView.as_view(), name="create_document"),
    path("change_document/<int:pk>", ChangeDocumentView.as_view(), name="change_document"),
    path("delete_document/<int:pk>", DeleteDocumentView.as_view(), name="delete_document"),
    path("search/author", AuthorSearchView.as_view(), name="search_author"),
    path("search/tag", TagSearchView.as_view(), name="search_tag"),
    path("history/<int:id>/", browsing_history, name="history"),
    path("popular_knowledges/", get_popular_knowledges, name="popular_knowledges"),
    path("privacy/", PrivacyPolicyView.as_view(), name="privacy"),
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
    path("special_permission/<int:id>/", get_special_permission, name="special_permission"),
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
        'interview/<int:inter_pk>/questions/<int:quest_pk>/answer/<int:answer_pk>/add_subanswer',
        sub_answer_create_view,
        name='add_subanswer'
    ),
    path(
        'interview/<int:interview_pk>/question/<int:question_pk>/answer/<int:answer_pk>/answer_as_incorrect',
        set_answer_as_incorrect,
        name='set_answer_as_incorrect'
    ),
    path(
        'interview/answer/<int:proposal_pk>/new_answer_is_agreed',
        set_new_answer_is_agreed,
        name='set_new_answer_is_agreed'
    ),
    path(
        'interview/<int:interview_pk>/question/<int:question_pk>/answer/<int:answer_pk>/answer_is_agreed',
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

    path(
        'special_permissions/',
        SpecialPermissionsView.as_view(),
        name='special_permissions_page'
    ),
    path(
        'special_permissions/set_users_as_editor',
        set_users_as_editor,
        name='set_users_as_editor'
    ),
    path(
        'special_permissions/to_experts/<int:category_pk>',
        ExpertsCandidatesListView.as_view(),
        name='experts_candidates_page'
    ),
    path(
        'special_permissions/set_users_as_expert/<int:category_pk>',
        set_users_as_expert,
        name='set_users_as_expert'
    ),
    path(
        'special_permissions/to_admins/<int:category_pk>',
        AdminsCandidatesListView.as_view(),
        name='admins_candidates_page'
    ),
    path(
        'special_permissions/set_users_as_admin/<int:category_pk>',
        set_users_as_admin,
        name='set_users_as_admin'
    ),
    path(
        'special_permissions/candidates/<int:category_pk>/experts/<int:candidate_pk>/knowledge_list/',
        ExpertCandidateKnowledgeView.as_view(),
        name='expert_candidate_knowledge'
    ),
    path(
        'special_permissions/candidates/<int:category_pk>/admins/<int:candidate_pk>/knowledge_list/',
        AdminCandidateKnowledgeView.as_view(),
        name='admin_candidate_knowledge'
    ),
    path(
        'my_special_permissions/',
        UsersSpecialPermissionsView.as_view(),
        name='my_special_permissions'
    ),
    path(
        'special_permissions/delete',
        SpecialPermissionsDeleteView.as_view(),
        name='delete_special_permissions_page'
    ),
    path(
        'special_permissions/experts_for_delete/<int:category_pk>',
        ExpertsPermissionsDeleteView.as_view(),
        name='deleting_experts_permissions_page'
    ),
    path(
        'special_permissions/experts_for_delete/<int:category_pk>/delete',
        delete_competence_expert,
        name='delete_competence_expert'
    ),
    path(
        'special_permissions/experts_for_delete/<int:category_pk>/expert/<int:expert_pk>/knowledge',
        ExpertKnowledgeView.as_view(),
        name='expert_knowledge_page'
    ),
    path(
        'special_permissions/delete/editors',
        delete_editor_permissions,
        name='delete_editor_permissions'
    ),
    path(
        'special_permissions/admins_for_delete/<int:category_pk>',
        AdminsPermissionsDeleteView.as_view(),
        name='deleting_admins_permissions_page'
    ),
    path(
        'special_permissions/admins_for_delete/<int:category_pk>/delete',
        delete_competence_admin,
        name='delete_competence_admin'
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
    path('profile/settings/', ParameterSettingsView.as_view(), name='parameter_settings'),
    path('profile/settings/update', update_user_settings, name='update_settings'),
    path('get_required_tr', get_required_tr, name='get_required_tr'),
    path('get_required_rz', get_required_rz, name='get_required_rz'),
    path('tree/search_results', search_by_tree_view, name='search_by_tree'),
    path('tree/search_results/advance', advance_search_by_tree_view, name='advance_search_by_tree'),
    path(
        'relations/preparing/create_stage',
        PreparingRelationsCreateView.as_view(),
        name='preparing_relations_create_page'
    ),
    path(
        'relations/preparing/update_stage',
        PreparingRelationsUpdateView.as_view(),
        name='preparing_relations_update_page'
    ),
    path(
        'relations/preparing/expertise_stage',
        PreparingRelationsExpertiseView.as_view(),
        name='preparing_relations_expertise_page'
    ),
    path(
        'relations/preparing/expertise_stage/expertise',
        RelationsExpertisePageView.as_view(),
        name='relation_expertise_page'
    ),
    path(
        'relation/expertise/<int:relation_pk>',
        relation_expertise_view,
        name='expertise_relation'
    ),
    path(
        'relations/preparing/publication_stage',
        PreparingRelationsPublicationView.as_view(),
        name='preparing_relations_publication_page'
    ),
    path(
        'relations/preparing/create_stage/new_relation',
        RelationCreatePageView.as_view(),
        name='relation_create_page'
    ),
    path(
        'relations/preparing/check_related',
        check_related,
        name='check_related'
    ),
    path(
        'relations/preparing/related_tz',
        get_related_tz,
        name='get_related_tz'
    ),
    path(
        'relations/create',
        relation_create_view,
        name='create_relation'
    ),
    path(
        'relation/delete',
        relation_delete_view,
        name='delete_relation'
    ),
    path(
        'relation/preparing/additional_knowledge/create',
        create_additional_knowledge,
        name='create_additional_knowledge'
    ),
    path(
        'relation/preparing/additional_knowledge/update/<int:kn_pk>',
        additional_knowledge_update_view,
        name='update_additional_knowledge_page'
    ),
    path(
        'relations/preparing/update_stage/update_relation',
        RelationUpdatePageView.as_view(),
        name='relation_update_page'
    ),
    path(
        'relations/update/<int:relation_pk>',
        relation_update_view,
        name='relation_update'
    ),
    path(
        'relations/preparing/publication_stage/publication_relation',
        RelationsPublicationPageView.as_view(),
        name='relation_publication_page'
    ),
    path(
        'relations/publication/<int:relation_pk>',
        relation_publication_view,
        name='relation_publication'
    ),
    path("filling_tables/<int:pk>/", FillingTablesView.as_view(), name="filling_tables"),
    path("save_zn_to_cell_in_table_from_request/", save_zn_to_cell_in_table_from_request, name="save_zn_to_cell_in_table_from_request"),
    path("get_cell_for_table/", get_cell_for_table, name="get_cell_for_table"),
    path(
        'main_znanie_in_constructor_create/<type_of_zn>/',
        MainZnInConstructorCreateView.as_view(),
        name="main_znanie_in_constructor_create"
    ),
    path('znaniya_for_constructor/', ZnaniyaForConstructorView.as_view(), name="znaniya_for_constructor"),
    path("delete_table/", delete_table, name="delete_table"),
    path("delete_row_or_column/", delete_row_or_column, name="delete_row_or_column"),
    path("show_filling_tables_page/", show_filling_tables_page, name="show_filling_tables_page"),
    path("delete_element_of_relation/", delete_element_of_relation, name="delete_element_of_relation"),
    path("get_answers_to_selected_question_of_quiz/", get_answers_to_selected_question_of_quiz,
         name="get_answers_to_selected_question_of_quiz"),
    path("row_and_column_existence/", row_and_column_existence, name="row_and_column_existence"),
    path(
        "delete_answers_or_questions_to_quiz/",
        delete_answers_or_questions_to_quiz,
        name="delete_answers_or_questions_to_quiz"
    ),
    path(
        'rel_in_tree_constructor/create/',
        get_tr_for_create_relation_in_tree_constructor,
        name="rel_in_tree_constructor_create"
    ),
    path("get_rel_zn_in_tree_constructor_from_request/", get_rel_zn_in_tree_constructor_from_request, name="get_rel_zn_in_tree_constructor_from_request"),
    path("quiz_constructor/<int:pk>/", QuizConstructorView.as_view(), name="quiz_constructor"),
    path("tree_constructor/<type>/<int:pk>/", TreeConstructorView.as_view(), name="tree_constructor"),
    path("table_constructor/<int:pk>/", TableConstructorView.as_view(), name="table_constructor"),
    path("save_rel_in_tree_constructor/", save_rel_in_tree_constructor, name="save_rel_in_tree_constructor"),
    path("make_copy_of_algorithm/", make_copy_of_algorithm, name="make_copy_of_algorithm"),
    path("delete_relation_in_tree_constructor/", delete_relation_in_tree_constructor, name="delete_relation_in_tree_constructor"),
    path("rel_in_tree_constructor/edit/", get_tr_for_edit_relation_in_tree_constructor,
         name="rel_in_tree_constructor_edit"),
    path("edit_znanie_in_tree_constructor/", edit_znanie_in_tree_constructor,
         name="edit_znanie_in_tree_constructor"),
    path("create_zn_in_tree_constructor/", create_zn_in_tree_constructor,
         name="create_zn_in_tree_constructor"),
    path("is_current_user_creator_of_zn/", is_current_user_creator_of_zn,
         name="is_current_user_creator_of_zn"),
    path("delete_complex_zn/", delete_complex_zn,
         name="delete_complex_zn"),
    path("create_zn_for_cell/", create_zn_for_cell,
         name="create_zn_for_cell"),
    path("check_algorithm_correctness_from_request/", check_algorithm_correctness_from_request,
         name="check_algorithm_correctness_from_request"),
    path("relation_in_table_create_update_view/", relation_in_table_create_update_view,
         name="relation_in_table_create_update_view"),
    path("element_of_group_in_table_create_update_view/", element_of_group_in_table_create_update_view,
         name="element_of_group_create_update_in_table"),
    path("edit_main_zn_in_constructor/", edit_main_zn_in_constructor,
         name="edit_main_zn_in_constructor"),
    path("get_order_of_relation/", get_order_of_relation,
         name="get_order_of_relation"),
    path("delete_algorithm/", delete_algorithm,
         name="delete_algorithm"),
    path("delete_zn_in_cell_in_table/", delete_zn_in_cell_in_table,
         name="delete_zn_in_cell_in_table"),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
