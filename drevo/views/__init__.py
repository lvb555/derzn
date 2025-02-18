from .algorithm_detail_view import AlgorithmDetailView, AlgorithmResultAdd, EditAlgorithm
from .algorithm_list_view import AlgorithmListView
from .author_detail_view import AuthorDetailView
from drevo.views.quiz_list_view import QuizListView
from .quiz_detail_view import QuizDetailView
from .quiz_result_processing_view import QuizResultAdd
from .authors_list_view import AuthorsListView
from .comment_page_view import CommentPageView
from .comment_send_view import CommentSendView
from .drevo_list_view import DrevoListView
from .drevo_view import DrevoView
from .knowledge_view import KnowledgeView
from .expert_work.views import (
    QuestionExpertWorkPage,
    propose_answer,
    sub_answer_create_view,
    ExpertProposalDeleteView,
    set_answer_as_incorrect,
    set_answer_is_agreed,
    set_new_answer_is_agreed,
    proposal_update_view,
)
from .admin_interview_work.views import (
    AllInterviewView,
    InterviewQuestionsView,
    question_admin_work_view,
    AdminEditingKnowledgeView,
    NotifyExpertsView,
)
from .favourite_processing_view import FavouriteProcessView
from .favourites_view import FavouritesView
from .algorithm_check_correctness_view import check_algorithm_correctness_from_request
from .zn_constructors.supplementary_functions import make_copy_of_algorithm
from .zn_constructors.algorithm_constructor_view import delete_algorithm
from .zn_constructors.tree_constructor_view import (
    TreeConstructorView,
    get_tr_for_create_relation_in_tree_constructor,
    get_rel_zn_in_tree_constructor_from_request,
    save_rel_in_tree_constructor,
    delete_relation_in_tree_constructor,
    get_tr_for_edit_relation_in_tree_constructor,
    edit_znanie_in_tree_constructor,
    create_zn_in_tree_constructor,
    is_current_user_creator_of_zn,
    get_order_of_relation,
)
from .zn_constructors.general_views import (
    ZnaniyaForConstructorView,
    MainZnInConstructorCreateView,
    UnprocessedSuggestionsTreeView,
    edit_main_zn_in_constructor,
    delete_complex_zn
)
from .zn_constructors.quiz_constructor_view import (
    QuizConstructorView,
    question_create_update_in_quiz,
    answer_create_update_in_quiz,
    answers_in_quiz_existence,
    delete_answers_or_questions_to_quiz,
    delete_quiz,
    get_answers_to_selected_question_of_quiz,
)
from .friends_added_view import friends_added_view
from .friends_view import friends_view
from .glossary_list_view import GlossaryListView
from .knowledge_grade_view import KnowledgeFormView
from .labels_list_view import LabelsListView
from .new_knowledge_list_view import NewKnowledgeListView
from .search_author_view import AuthorSearchView
from .search_knowledge_view import KnowledgeSearchView
from .search_tag_view import TagSearchView
from .znanie_by_label_view import ZnanieByLabelView
from .znanie_detail_view import ZnanieDetailView
from .znanie_rating_view import ZnanieRatingView
from .znanie_send_view import send_znanie
from .knowledge_grade_statistic_view import KnowledgeStatisticFormView
from .group_knowledge_grade_view import GroupKnowledgeView
from .infographics_view import InfographicsView
from .my_knowledge_grade_view import my_knowledge_grade
from .knowledges_grades_view import knowledges_grades
from .group_infographics_view import GroupInfographicsView
from .group_knowledge_grade_statistics import GroupKnowledgeStatisticsView
from .parameter_settings_view import ParameterSettingsView, update_user_settings
from .special_permissions_work.view import (
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
from .special_permissions_work.delete_permissions_views import (
    SpecialPermissionsDeleteView,
    ExpertsPermissionsDeleteView,
    delete_competence_expert,
    ExpertKnowledgeView,
    delete_editor_permissions,
    AdminsPermissionsDeleteView,
    delete_competence_admin,
)
from .knowledge_types_view import KnowledgeTypesView
from .relation_types_view import RelationTypesView
from .relationship_tr_tz_view import get_required_tr, get_required_rz
from .search_by_tree_view import search_by_tree_view, advance_search_by_tree_view

from .relations_preparing_work import (
    create_additional_knowledge,
    additional_knowledge_update_view,
    check_related,
    get_related_tz,
    PreparingRelationsExpertiseView,
    PreparingRelationsPublicationView,
    PreparingRelationsUpdateView,
    PreparingRelationsCreateView,
    RelationCreatePageView,
    relation_create_view,
    relation_delete_view,
    RelationUpdatePageView,
    relation_update_view,
    RelationsExpertisePageView,
    relation_expertise_view,
    RelationsPublicationPageView,
    relation_publication_view,
)

from .document_text_template import (
    DocumentTextTemplateEdit,
    DocumentObjectProcessingView,
    ObjectsTree,
    save_text_template_view,
    document_object_deletion_view,
    object_tree_correctnes_check_view
)

# __all__ = [
#     "AuthorDetailView",
#     "AuthorsListView",
#     "AlgorithmListView",
#     "AlgorithmDetailView",
#     "AlgorithmResultAdd",
#     "EditAlgorithm",
#     "CommentPageView",
#     "CommentSendView",
#     "DrevoListView",
#     "DrevoView",
#     "KnowledgeView",
#     "GlossaryListView",
#     "LabelsListView",
#     "ZnanieByLabelView",
#     "ZnanieDetailView",
#     "ZnanieRatingView",
#     "NewKnowledgeListView",
#     "KnowledgeSearchView",
#     "AuthorSearchView",
#     "TagSearchView",
#     "KnowledgeFormView",
#     "FavouritesView",
#     "FavouriteProcessView",
#     "answers_in_quiz_existence",
#     "ZnaniyaForConstructorView",
#     "MainZnInConstructorCreateView",
#     "FillingTablesView",
#     "get_cell_for_table",
#     "save_zn_to_cell_in_table_from_request",
#     "delete_table",
#     "delete_row_or_column",
#     "row_and_column_existence",
#     "show_filling_tables_page",
#     "delete_element_of_relation",
#     "friends_view",
#     "friends_added_view",
#     "friends_invite_view",
#     "FavouriteProcessView",
#     "propose_answer",
#     "QuestionExpertWorkPage",
#     "send_znanie",
#     "QuizListView",
#     "KnowledgeStatisticFormView",
#     'QuizResultAdd',
#     "GroupKnowledgeView",
#     'QuizDetailView',
#     'question_create_update_in_quiz',
#     'answer_create_update_in_quiz',
#     "delete_answers_or_questions_to_quiz",
#     "delete_quiz",
#     "get_answers_to_selected_question_of_quiz",
#     "InfographicsView",
#     "my_knowledge_grade",
#     "knowledges_grades",
#     "GroupInfographicsView",
#     "GroupKnowledgeStatisticsView",
#     'ParameterSettingsView',
#     'update_user_settings',
#     'sub_answer_create_view',
#     'ExpertProposalDeleteView',
#     'set_answer_as_incorrect',
#     'set_answer_is_agreed',
#     'proposal_update_view',
#     'SpecialPermissionsView',
#     'set_users_as_editor',
#     'ExpertsCandidatesListView',
#     'set_users_as_expert',
#     'AdminsCandidatesListView',
#     'set_users_as_admin',
#     'UsersSpecialPermissionsView',
#     'set_new_answer_is_agreed',
#     'ExpertCandidateKnowledgeView',
#     'AdminCandidateKnowledgeView',
#     'KnowledgeTypesView',
#     'RelationTypesView',
#     'SpecialPermissionsDeleteView',
#     'ExpertsPermissionsDeleteView',
#     'delete_competence_expert',
#     'ExpertKnowledgeView',
#     'delete_editor_permissions',
#     'AdminsPermissionsDeleteView',
#     'delete_competence_admin',
#     'get_required_tr',
#     'get_required_rz',
#     'search_by_tree_view',
#     'advance_search_by_tree_view',
#     'PreparingRelationsCreateView',
#     'PreparingRelationsUpdateView',
#     'PreparingRelationsExpertiseView',
#     'PreparingRelationsPublicationView',
#     'RelationCreatePageView',
#     'check_related',
#     'relation_create_view',
#     'relation_delete_view',
#     'create_additional_knowledge',
#     'get_related_tz',
#     'additional_knowledge_update_view',
#     'RelationUpdatePageView',
#     'relation_update_view',
#     'RelationsExpertisePageView',
#     'relation_expertise_view',
#     'RelationsPublicationPageView',
#     'relation_publication_view',
#     'get_tr_for_create_relation_in_tree_constructor',
#     'get_rel_zn_in_tree_constructor_from_request',
#     'TreeConstructorView',
#     'TableConstructorView',
#     'QuizConstructorView',
#     'save_rel_in_tree_constructor',
#     'make_copy_of_algorithm',
#     'delete_relation_in_tree_constructor',
#     'get_tr_for_edit_relation_in_tree_constructor',
#     'edit_znanie_in_tree_constructor',
#     'create_zn_in_tree_constructor',
#     'is_current_user_creator_of_zn',
#     'delete_complex_zn',
#
#     'check_algorithm_correctness_from_request',
#     'relation_in_table_create_update_view',
#     'element_of_group_in_table_create_update_view',
#     'edit_main_zn_in_constructor',
#     'get_order_of_relation',
#     'delete_algorithm',
#     'delete_zn_in_cell_in_table',
# ]
