from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from drevo.views.interviews_statistics_view import dimensional_distributions_1, dimensional_distributions_2
from drevo.views.interviews_all_view import interviews_all
from drevo.views.interview_table_view import interview_table
from drevo.views.developer_view import developer_view
from drevo.views.interviews_view import interview_view
from drevo.views.my_interview_view import my_interview_view
from drevo.views.comment_send_view import toggle_reaction
from .urls_constructor import urlpatterns as urls_constructor
from .views import (AdminsPermissionsDeleteView, AlgorithmDetailView,
                    AlgorithmListView, AlgorithmResultAdd, AuthorDetailView,
                    AuthorSearchView, AuthorsListView, CommentPageView,
                    CommentSendView, DocumentTextTemplateEdit, DrevoListView,
                    DrevoView, EditAlgorithm, ExpertKnowledgeView,
                    ExpertsPermissionsDeleteView, FavouriteProcessView,
                    FavouritesView, GlossaryListView, GroupInfographicsView,
                    GroupKnowledgeStatisticsView, GroupKnowledgeView,
                    InfographicsView, KnowledgeFormView, KnowledgeSearchView,
                    KnowledgeStatisticFormView, KnowledgeTypesView,
                    KnowledgeView, LabelsListView, NewKnowledgeListView,
                    ObjectsTree, ParameterSettingsView,
                    PreparingRelationsCreateView,
                    PreparingRelationsExpertiseView,
                    PreparingRelationsPublicationView,
                    PreparingRelationsUpdateView, QuestionExpertWorkPage,
                    QuizDetailView, QuizListView, QuizResultAdd,
                    RelationCreatePageView, RelationsExpertisePageView,
                    RelationsPublicationPageView, RelationTypesView,
                    RelationUpdatePageView, SpecialPermissionsDeleteView,
                    TagSearchView, ZnanieByLabelView, ZnanieDetailView,
                    ZnanieRatingView, about_proj,
                    additional_knowledge_update_view,
                    advance_search_by_tree_view, check_related,
                    create_additional_knowledge, delete_competence_admin,
                    delete_competence_expert, delete_editor_permissions,
                    DocumentObjectProcessingView,
                    document_object_deletion_view,
                    object_tree_correctnes_check_view,
                    friends_added_view,
                    friends_view, get_related_tz, get_required_rz,
                    get_required_tr, knowledge_feed_view, knowledges_grades,
                    messages_feed_view, my_knowledge_grade,
                    relation_create_view, relation_delete_view,
                    relation_expertise_view, relation_publication_view,
                    relation_update_view, save_text_template_view,
                    search_by_tree_view, send_message_view, send_znanie,
                    update_user_settings)
from .views.admin_interview_work.views import (AdminEditingKnowledgeView,
                                               AllInterviewView,
                                               InterviewQuestionsView,
                                               NotifyExpertsView,
                                               question_admin_work_view)
from .views.appeal_in_support import appeal
from .views.browsing_history import browsing_history
from .views.cookie_acceptance_process_view import CookieAcceptance
from drevo.views.participations.create_participation import CreateParticipationView
from drevo.views.participations.participation_in_the_discussion_view import ParticipationInTheDiscussionView
from .views.search_knowledge_view import search_knowledge_by_name
from .views.site_pages import site_pages_view, site_page_view, create_new_zn, search_page
from .views.editorial_staff import editorial_staff_view, update_roles, update_user_permissions
from .views.expert_work.views import (ExpertProposalDeleteView,
                                      proposal_update_view, propose_answer,
                                      set_answer_as_incorrect,
                                      set_answer_is_agreed,
                                      set_new_answer_is_agreed,
                                      sub_answer_create_view)
from .views.interview_and_proposal import my_interview, my_proposal
from .views.klz_all_knowledges import klz_all
from .views.knowledge_tp_view import (DirectorKnowledgeProcess,
                                      ExpertKnowledgeProcess,
                                      KlzKnowledgeProcess,
                                      KnowledgeChangeStatus,
                                      KnowledgeCreateView, KnowledgeUpdateView,
                                      RedactorKnowledgeProcess,
                                      UserKnowledgeProcessView)
from .views.my_favourites import my_favourites
from .views.my_knowledge import my_expertise, my_knowledge, my_preknowledge
from .views.new_knowledges import new_knowledge
from .views.popular_knowledges import get_popular_knowledges
from .views.privacy_policy import PrivacyPolicyView
from .views.public_people import public_human, public_people_view
from .views.questions import questions_and_check_answers, save_answer
from .views.quiz_result import show_quiz_result
from .views.special_permissions_for_public import get_special_permission
from .views.special_permissions_work.view import (AdminCandidateKnowledgeView,
                                                  AdminsCandidatesListView,
                                                  ExpertCandidateKnowledgeView,
                                                  ExpertsCandidatesListView,
                                                  SpecialPermissionsView,
                                                  UsersSpecialPermissionsView,
                                                  set_users_as_admin,
                                                  set_users_as_editor,
                                                  set_users_as_expert)
from .views.subscribe_to_author_view import sub_by_author
from .views.subscription_by_category_view import sub_by_category
from .views.subscription_by_tag_view import sub_by_tag
from .views.user_suggestion_view import UserSuggestionView
from .views.users_documents import (ChangeDocumentView, CreateDocumentView,
                                    DeleteDocumentView)

urlpatterns = [
    # Общие
    path("", DrevoView.as_view(), name="drevo"),  # глав страница
    path("about/", about_proj.AboutView.as_view(), name="about_proj"),  # о проекте
    path("appeal/", appeal, name="appeal"),  # обратная связь
    path("klz_/", klz_all, name="clz"),  # клуб любителей знаний
    path(
        "klz/", KlzKnowledgeProcess.as_view(), name="klz"
    ),  # еще один клуб любителей знаний :)
    path("developer/", developer_view, name="developer_page"),  # разработчики
    path("glossary/", GlossaryListView.as_view(), name="glossary"),  # Глоссарий
    path("privacy/", PrivacyPolicyView.as_view(), name="privacy"),  # Политика обработки
    path(
        "cookie_acceptance/", CookieAcceptance.as_view()
    ),  # сохраняет согласие с куками в БД
    # --------------------------------------------------------------------------------------------------
    # Дерево знаний
    path("knowledge/", KnowledgeView.as_view(), name="knowledge"),  # дерево знаний
    path("tree/search_results", search_by_tree_view, name="search_by_tree"),
    # служебные для работы поиска в дереве знаний
    path(
        "tree/search_results/advance",
        advance_search_by_tree_view,
        name="advance_search_by_tree",
    ),  # служебн
    # --------------------------------------------------------------------------------------------------
    # Разные списки знаний
    path(
        "category/<int:pk>", DrevoListView.as_view(), name="drevo_type"
    ),  # знания по категории???
    path(
        "new_knowledge/", NewKnowledgeListView.as_view(), name="new_knowledge"
    ),  # новые знания
    path(
        "popular_knowledges/", get_popular_knowledges, name="popular_knowledges"
    ),  # популярные знания
    path("favourites/", FavouritesView.as_view(), name="favourites"),  # избранное
    # --------------------------------------------------------------------------------------------------
    # Оценка знаний
    path("knowledges_grades/", knowledges_grades, name="knowledges_grades"),
    path(
        "my_knowledge_grade/<int:id>/", my_knowledge_grade, name="my_knowledge_grade"
    ),  # мои оценки знаний
    # --------------------------------------------------------------------------------------------------
    # знания и связи по виду.....
    path(
        "knowledge/types/<int:type_pk>",
        KnowledgeTypesView.as_view(),
        name="knowledge_type",
    ),  # все знания вида ...
    path(
        "relations/types/<int:type_pk>",
        RelationTypesView.as_view(),
        name="relation_type",
    ),  # все связи вида ...
    # --------------------------------------------------------------------------------------------------
    # публичные люди
    path("public_people", public_people_view, name="public_people"),
    path("public_people/<int:id>/", public_human, name="public_human"),
    # --------------------------------------------------------------------------------------------------
    # теги
    path("labels/", LabelsListView.as_view(), name="labels"),
    path("label/<int:pk>", ZnanieByLabelView.as_view(), name="zlabel"),
    # --------------------------------------------------------------------------------------------------
    # авторы
    path("authors/", AuthorsListView.as_view(), name="authors"),
    path("author/<int:pk>", AuthorDetailView.as_view(), name="author"),
    # --------------------------------------------------------------------------------------------------
    # связано с текущим пользователем
    path(
        "history/<int:id>/", browsing_history, name="history"
    ),  # история просмотров user-id
    path(
        "subscribe_to_author/<int:id>/", sub_by_author, name="subscribe_to_author"
    ),  # подписка на авторов
    path("subscription_by_tag/<int:id>/", sub_by_tag, name="subscription_by_tag"),
    path(
        "subscription_by_category/<int:id>/",
        sub_by_category,
        name="subscription_by_category",
    ),
    path("new_knowledges/<int:id>/", new_knowledge, name="new_knowledges"),
    path("my_favourites/<int:id>/", my_favourites, name="my_favourites"),
    path("my_knowledge/<int:id>/", my_knowledge, name="my_knowledge"),
    path("my_preknowledge/<int:id>/", my_preknowledge, name="my_preknowledge"),
    path("my_expertise/<int:id>/", my_expertise, name="my_expertise"),
    path("my__interview/<int:id>/", my_interview, name="my_interview_profile"),
    path(
        "special_permission/<int:id>/",
        get_special_permission,
        name="special_permission",
    ),
    path("my_proposal/<int:id>/", my_proposal, name="my_proposal"),
    # --------------------------------------------------------------------------------------------------
    # настройки параметров
    path(
        "profile/settings/", ParameterSettingsView.as_view(), name="parameter_settings"
    ),
    path("profile/settings/update", update_user_settings, name="update_settings"),
    # --------------------------------------------------------------------------------------------------
    # Знание - работа с ним
    path("znanie/<int:pk>", ZnanieDetailView.as_view(), name="zdetail"),
    path(
        "znanie/<int:pk>/suggestions",
        UserSuggestionView.as_view(),
        name="create-suggestion",
    ),
    path("znanie/<int:pk>/questions_user", save_answer, name="questions_user"),
    path(
        "znanie/<int:pk>/questions_and_check_answers",
        questions_and_check_answers,
        name="questions_and_check_answers",
    ),
    path("znanie/<int:pk>/favourite", FavouriteProcessView.as_view()),
    path("znanie/<int:pk>/comments/", CommentPageView.as_view()),
    path("znanie/<int:pk>/comments/send/", CommentSendView.as_view()),
    path(
        "znanie/<int:pk>/vote/<str:vote>/", ZnanieRatingView.as_view(), name="znrating"
    ),
    path("znanie/<int:pk>/message/send/", send_znanie, name="zsend_mes"),
    path("znanie/<int:pk>/grade/", KnowledgeFormView.as_view(), name="grade"),
    path(
        "znanie/<int:pk>/grade/statistic",
        KnowledgeStatisticFormView.as_view(),
        name="grade_statistic",
    ),
    path(
        "znanie/<int:pk>/grade/group",
        GroupKnowledgeView.as_view(),
        name="group_knowledge",
    ),
    path(
        "znanie/<int:pk>/grade/group/infographics",
        GroupInfographicsView.as_view(),
        name="grade_group_infographics",
    ),
    path(
        "znanie/<int:pk>/grade/group/statistics",
        GroupKnowledgeStatisticsView.as_view(),
        name="grade_group_statistics",
    ),
    path(
        "znanie/<int:pk>/grade/infographics",
        InfographicsView.as_view(),
        name="grade_infographics",
    ),
    path(
        "znanie/<int:doc_pk>/document-template/edit-text/<int:text_pk>",
        DocumentTextTemplateEdit.as_view(),
        name="edit_text_template",
    ),
    path(
        "znanie/<int:doc_pk>/document-template/document_object_processing",
        DocumentObjectProcessingView.as_view(),
    ),
    path(
        "znanie/<int:doc_pk>/document-template/document_object_deletion",
        document_object_deletion_view
    ),
    path(
        "znanie/<int:doc_pk>/document-template/object_tree_correctness",
        object_tree_correctnes_check_view
    ),
    path(
        "znanie/<int:doc_pk>/document-template/object-select",
        ObjectsTree.as_view(),
        name="select_object_from_tree",
    ),
    path(
        "znanie/<int:doc_pk>/document-template/save-text-template",
        save_text_template_view,
        name="save_text_template",
    ),
    # --------------------------------------------------------------------------------------------------
    # квизы
    path("all_quizzes/", QuizListView.as_view(), name="all_quizzes"),
    path("quiz/<int:pk>", QuizDetailView.as_view(), name="quiz"),
    path("quiz/<int:pk>/quiz_result/", QuizResultAdd.as_view()),
    path("quiz/<int:pk>/vote/<str:vote>", ZnanieRatingView.as_view()),
    path("quiz/<int:pk>/favourite", FavouriteProcessView.as_view()),
    path("quiz_results/<int:id>/", show_quiz_result, name="show_quiz_result"),
    # --------------------------------------------------------------------------------------------------
    # Алгоритмы
    path("all_algorithms/", AlgorithmListView.as_view(), name="all_algorithms"),
    path("algorithm/<int:pk>", AlgorithmDetailView.as_view(), name="algorithm"),
    path("algorithm/<int:pk>/algorithm_result/", AlgorithmResultAdd.as_view()),
    path("algorithm/<int:pk>/edit_algorithm/", EditAlgorithm.as_view()),
    # --------------------------------------------------------------------------------------------------
    # Поиск...
    path("search/knowledge", KnowledgeSearchView.as_view(), name="search_knowledge"),
    path("search/knowledge_by_name", search_knowledge_by_name, name="search_knowledge_name"),
    path("search/author", AuthorSearchView.as_view(), name="search_author"),
    path("search/tag", TagSearchView.as_view(), name="search_tag"),
    # --------------------------------------------------------------------------------------------------
    # Дерево страниц сайта 
    path("site_pages/", site_pages_view, name="site_pages"),
    path("site_pages/<int:pk>/", site_page_view, name="site_page"),
    path("site_pages/create_new_zn/", create_new_zn, name="create_new_zn"),
    path('site_pages/search/', search_page, name='search_page'),
    # --------------------------------------------------------------------------------------------------
    # документ????
    path(
        "create_document/<int:pk>", CreateDocumentView.as_view(), name="create_document"
    ),
    path(
        "change_document/<int:pk>", ChangeDocumentView.as_view(), name="change_document"
    ),
    path(
        "delete_document/<int:pk>", DeleteDocumentView.as_view(), name="delete_document"
    ),
    # --------------------------------------------------------------------------------------------------
    # интервью
    path("my_interview/", my_interview_view, name="my_interview"),
    path("interview/<int:pk>/", interview_view, name="interview"),
    path("interview_table/<int:id>/", interview_table, name="interview_table"),
    path("interviews_all", interviews_all, name="interviews_all"),
    path("dimensional_distributions_1/<int:id>/", dimensional_distributions_1, name="dimensional_distributions_1"),
    path("dimensional_distributions_2/<int:id>/", dimensional_distributions_2, name="dimensional_distributions_2"),

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
        "interview/<int:inter_pk>/questions/<int:quest_pk>/answer/<int:answer_pk>/add_subanswer",
        sub_answer_create_view,
        name="add_subanswer",
    ),
    path(
        "interview/<int:interview_pk>/question/<int:question_pk>/answer/<int:answer_pk>/answer_as_incorrect",
        set_answer_as_incorrect,
        name="set_answer_as_incorrect",
    ),
    path(
        "interview/answer/<int:proposal_pk>/new_answer_is_agreed",
        set_new_answer_is_agreed,
        name="set_new_answer_is_agreed",
    ),
    path(
        "interview/<int:interview_pk>/question/<int:question_pk>/answer/<int:answer_pk>/answer_is_agreed",
        set_answer_is_agreed,
        name="set_answer_is_agreed",
    ),
    path(
        "interview/proposal/<int:proposal_pk>/update",
        proposal_update_view,
        name="proposal_update",
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
        name="admin_knowledge_edit",
    ),
    path(
        "admin/interview/<int:inter_pk>/questions/<int:quest_pk>/notify_experts/",
        NotifyExpertsView.as_view(),
        name="admin_notify_experts",
    ),
    # --------------------------------------------------------------------------------------------------
    # спец права - не работает???
    path(
        "special_permissions/",
        SpecialPermissionsView.as_view(),
        name="special_permissions_page",
    ),
    path(
        "special_permissions/set_users_as_editor",
        set_users_as_editor,
        name="set_users_as_editor",
    ),
    path(
        "special_permissions/to_experts/<int:category_pk>",
        ExpertsCandidatesListView.as_view(),
        name="experts_candidates_page",
    ),
    path(
        "special_permissions/set_users_as_expert/<int:category_pk>",
        set_users_as_expert,
        name="set_users_as_expert",
    ),
    path(
        "special_permissions/to_admins/<int:category_pk>",
        AdminsCandidatesListView.as_view(),
        name="admins_candidates_page",
    ),
    path(
        "special_permissions/set_users_as_admin/<int:category_pk>",
        set_users_as_admin,
        name="set_users_as_admin",
    ),
    path(
        "special_permissions/candidates/<int:category_pk>/experts/<int:candidate_pk>/knowledge_list/",
        ExpertCandidateKnowledgeView.as_view(),
        name="expert_candidate_knowledge",
    ),
    path(
        "special_permissions/candidates/<int:category_pk>/admins/<int:candidate_pk>/knowledge_list/",
        AdminCandidateKnowledgeView.as_view(),
        name="admin_candidate_knowledge",
    ),
    path(
        "my_special_permissions/",
        UsersSpecialPermissionsView.as_view(),
        name="my_special_permissions",
    ),
    path(
        "special_permissions/delete",
        SpecialPermissionsDeleteView.as_view(),
        name="delete_special_permissions_page",
    ),
    path(
        "special_permissions/experts_for_delete/<int:category_pk>",
        ExpertsPermissionsDeleteView.as_view(),
        name="deleting_experts_permissions_page",
    ),
    path(
        "special_permissions/experts_for_delete/<int:category_pk>/delete",
        delete_competence_expert,
        name="delete_competence_expert",
    ),
    path(
        "special_permissions/experts_for_delete/<int:category_pk>/expert/<int:expert_pk>/knowledge",
        ExpertKnowledgeView.as_view(),
        name="expert_knowledge_page",
    ),
    path(
        "special_permissions/delete/editors",
        delete_editor_permissions,
        name="delete_editor_permissions",
    ),
    path(
        "special_permissions/admins_for_delete/<int:category_pk>",
        AdminsPermissionsDeleteView.as_view(),
        name="deleting_admins_permissions_page",
    ),
    path(
        "special_permissions/admins_for_delete/<int:category_pk>/delete",
        delete_competence_admin,
        name="delete_competence_admin",
    ),
    # --------------------------------------------------------------------------------------------------
    # Друзья, лента и обмен сообщениями - не работает?????
    # друзья
    path("friends/", friends_view, name="friends"),
    path("friends/friends_added/", friends_added_view, name="friends_added"),
    # path("friends/friends_invite/", friends_invite_view, name="friends_invite"),
    # Лента знаний
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
    path("send-message/", send_message_view.send_message, name="send_message"),
    path("messages-feed/", messages_feed_view.messages_feed, name="messages_feed"),
    path(
        "messages-feed/delete/<int:message_id>/",
        send_message_view.delete_message,
        name="delete_message",
    ),
    # --------------------------------------------------------------------------------------------------
    # что то про предзнания и знания????? (knowledge_tp_view)
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
    # --------------------------------------------------------------------------------------------------
    # Связи - (relation_preparing_work)
    path(
        "relations/preparing/create_stage",
        PreparingRelationsCreateView.as_view(),
        name="preparing_relations_create_page",
    ),
    path(
        "relations/preparing/update_stage",
        PreparingRelationsUpdateView.as_view(),
        name="preparing_relations_update_page",
    ),
    path(
        "relations/preparing/expertise_stage",
        PreparingRelationsExpertiseView.as_view(),
        name="preparing_relations_expertise_page",
    ),
    path(
        "relations/preparing/expertise_stage/expertise",
        RelationsExpertisePageView.as_view(),
        name="relation_expertise_page",
    ),
    path(
        "relation/expertise/<int:relation_pk>",
        relation_expertise_view,
        name="expertise_relation",
    ),
    path(
        "relations/preparing/publication_stage",
        PreparingRelationsPublicationView.as_view(),
        name="preparing_relations_publication_page",
    ),
    path(
        "relations/preparing/create_stage/new_relation",
        RelationCreatePageView.as_view(),
        name="relation_create_page",
    ),
    path("relations/preparing/check_related", check_related, name="check_related"),
    path("relations/preparing/related_tz", get_related_tz, name="get_related_tz"),
    path("relations/create", relation_create_view, name="create_relation"),
    path("relation/delete", relation_delete_view, name="delete_relation"),
    path(
        "relation/preparing/additional_knowledge/create",
        create_additional_knowledge,
        name="create_additional_knowledge",
    ),
    path(
        "relation/preparing/additional_knowledge/update/<int:kn_pk>",
        additional_knowledge_update_view,
        name="update_additional_knowledge_page",
    ),
    path(
        "relations/preparing/update_stage/update_relation",
        RelationUpdatePageView.as_view(),
        name="relation_update_page",
    ),
    path(
        "relations/update/<int:relation_pk>",
        relation_update_view,
        name="relation_update",
    ),
    path(
        "relations/preparing/publication_stage/publication_relation",
        RelationsPublicationPageView.as_view(),
        name="relation_publication_page",
    ),
    path(
        "relations/publication/<int:relation_pk>",
        relation_publication_view,
        name="relation_publication",
    ),
    # --------------------------------------------------------------------------------------------------
    # сотрудники редакции
    path("editorial_staff/", editorial_staff_view, name="editorial_staff"),
    path("editorial_staff/update_roles/", update_roles, name="update_roles"),
    path('editorial_staff/update-group-permissions/', update_user_permissions, name='update_group_permissions'),
    # --------------------------------------------------------------------------------------------------
    # служебное? возвращает json
    path("get_required_tr", get_required_tr, name="get_required_tr"),
    path("get_required_rz", get_required_rz, name="get_required_rz"),
    # ------------------------------------------------------------------------------------------------
    # эксперты - дискуссии
    path("participation_in_the_discussion/<int:pk>/", ParticipationInTheDiscussionView.as_view(),
         name="participation_in_the_discussion"),
    path("participation_in_the_discussion/create_participation", CreateParticipationView.as_view(),
         name="create_participation"),
    # реакции в комментариях
    path("react/<int:pk>/<str:reaction_type>", toggle_reaction, name="toggle_reaction"),
]

# пути для работы конструкторов знаний
urlpatterns += urls_constructor

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
