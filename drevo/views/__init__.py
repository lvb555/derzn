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
from .filling_tables import filling_tables, get_rows_and_columns, znanie_attributes, show_new_znanie, \
    show_filling_tables_page
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
from .parameter_settings_view import parameter_settings
from .special_permissions_work.view import (
    SpecialPermissionsView,
    set_users_as_editor,
    ExpertsCandidatesListView,
    set_users_as_expert,
    AdminsCandidatesListView,
    set_users_as_admin,
    UsersSpecialPermissionsView,
    ExpertCandidateKnowledgeView,
)

__all__ = [
    "AuthorDetailView",
    "AuthorsListView",
    "CommentPageView",
    "CommentSendView",
    "DrevoListView",
    "DrevoView",
    "KnowledgeView",
    "GlossaryListView",
    "LabelsListView",
    "ZnanieByLabelView",
    "ZnanieDetailView",
    "ZnanieRatingView",
    "NewKnowledgeListView",
    "KnowledgeSearchView",
    "AuthorSearchView",
    "TagSearchView",
    "KnowledgeFormView",
    "FavouritesView",
    "FavouriteProcessView",
    "filling_tables",
    "friends_view",
    "friends_added_view",
    "friends_invite_view",
    "FavouriteProcessView",
    "propose_answer",
    "QuestionExpertWorkPage",
    "send_znanie",
    "QuizListView",
    "KnowledgeStatisticFormView",
    'QuizResultAdd',
    "GroupKnowledgeView",
    'QuizDetailView',
    "InfographicsView",
    "my_knowledge_grade",
    "knowledges_grades",
    "GroupInfographicsView",
    "GroupKnowledgeStatisticsView",
    'parameter_settings',
    'sub_answer_create_view',
    'ExpertProposalDeleteView',
    'set_answer_as_incorrect',
    'set_answer_is_agreed',
    'proposal_update_view',
    'SpecialPermissionsView',
    'set_users_as_editor',
    'ExpertsCandidatesListView',
    'set_users_as_expert',
    'AdminsCandidatesListView',
    'set_users_as_admin',
    'UsersSpecialPermissionsView',
    'set_new_answer_is_agreed',
    'ExpertCandidateKnowledgeView',
]
