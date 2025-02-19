from drevo.views.quiz_list_view import QuizListView

from .admin_interview_work.views import (
    AdminEditingKnowledgeView,
    AllInterviewView,
    InterviewQuestionsView,
    NotifyExpertsView,
    question_admin_work_view,
)
from .algorithm_check_correctness_view import check_algorithm_correctness_from_request
from .algorithm_detail_view import AlgorithmDetailView, AlgorithmResultAdd, EditAlgorithm
from .algorithm_list_view import AlgorithmListView
from .author_detail_view import AuthorDetailView
from .authors_list_view import AuthorsListView
from .comment_page_view import CommentPageView
from .comment_send_view import CommentSendView
from .document_text_template import (
    DocumentObjectProcessingView,
    DocumentTextTemplateEdit,
    ObjectsTree,
    document_object_deletion_view,
    object_tree_correctnes_check_view,
    save_text_template_view,
)
from .drevo_list_view import DrevoListView
from .drevo_view import DrevoView
from .expert_work.views import (
    ExpertProposalDeleteView,
    QuestionExpertWorkPage,
    proposal_update_view,
    propose_answer,
    set_answer_as_incorrect,
    set_answer_is_agreed,
    set_new_answer_is_agreed,
    sub_answer_create_view,
)
from .favourite_processing_view import FavouriteProcessView
from .favourites_view import FavouritesView
from .friends_added_view import friends_added_view
from .friends_view import friends_view
from .glossary_list_view import GlossaryListView
from .group_infographics_view import GroupInfographicsView
from .group_knowledge_grade_statistics import GroupKnowledgeStatisticsView
from .group_knowledge_grade_view import GroupKnowledgeView
from .infographics_view import InfographicsView
from .knowledge_grade_statistic_view import KnowledgeStatisticFormView
from .knowledge_grade_view import KnowledgeFormView
from .knowledge_types_view import KnowledgeTypesView
from .knowledge_view import KnowledgeView
from .knowledges_grades_view import knowledges_grades
from .labels_list_view import LabelsListView
from .my_knowledge_grade_view import my_knowledge_grade
from .new_knowledge_list_view import NewKnowledgeListView
from .parameter_settings_view import ParameterSettingsView, update_user_settings
from .quiz_detail_view import QuizDetailView
from .quiz_result_processing_view import QuizResultAdd
from .relation_types_view import RelationTypesView
from .relations_preparing_work import (
    PreparingRelationsCreateView,
    PreparingRelationsExpertiseView,
    PreparingRelationsPublicationView,
    PreparingRelationsUpdateView,
    RelationCreatePageView,
    RelationsExpertisePageView,
    RelationsPublicationPageView,
    RelationUpdatePageView,
    additional_knowledge_update_view,
    check_related,
    create_additional_knowledge,
    get_related_tz,
    relation_create_view,
    relation_delete_view,
    relation_expertise_view,
    relation_publication_view,
    relation_update_view,
)
from .relationship_tr_tz_view import get_required_rz, get_required_tr
from .search_author_view import AuthorSearchView
from .search_by_tree_view import advance_search_by_tree_view, search_by_tree_view
from .search_knowledge_view import KnowledgeSearchView
from .search_tag_view import TagSearchView
from .special_permissions_work.delete_permissions_views import (
    AdminsPermissionsDeleteView,
    ExpertKnowledgeView,
    ExpertsPermissionsDeleteView,
    SpecialPermissionsDeleteView,
    delete_competence_admin,
    delete_competence_expert,
    delete_editor_permissions,
)
from .special_permissions_work.view import (
    AdminCandidateKnowledgeView,
    AdminsCandidatesListView,
    ExpertCandidateKnowledgeView,
    ExpertsCandidatesListView,
    SpecialPermissionsView,
    UsersSpecialPermissionsView,
    set_users_as_admin,
    set_users_as_editor,
    set_users_as_expert,
)
from .zn_constructors.algorithm_constructor_view import delete_algorithm
from .zn_constructors.general_views import (
    MainZnInConstructorCreateView,
    UnprocessedSuggestionsTreeView,
    ZnaniyaForConstructorView,
    delete_complex_zn,
    edit_main_zn_in_constructor,
)
from .zn_constructors.quiz_constructor_view import (
    QuizConstructorView,
    answer_create_update_in_quiz,
    answers_in_quiz_existence,
    delete_answers_or_questions_to_quiz,
    delete_quiz,
    get_answers_to_selected_question_of_quiz,
    question_create_update_in_quiz,
)
from .zn_constructors.supplementary_functions import make_copy_of_algorithm
from .zn_constructors.tree_constructor_view import (
    TreeConstructorView,
    create_zn_in_tree_constructor,
    delete_relation_in_tree_constructor,
    edit_znanie_in_tree_constructor,
    get_order_of_relation,
    get_rel_zn_in_tree_constructor_from_request,
    get_tr_for_create_relation_in_tree_constructor,
    get_tr_for_edit_relation_in_tree_constructor,
    is_current_user_creator_of_zn,
    save_rel_in_tree_constructor,
)
from .znanie_by_label_view import ZnanieByLabelView
from .znanie_detail_view import ZnanieDetailView
from .znanie_rating_view import ZnanieRatingView
from .znanie_send_view import send_znanie
