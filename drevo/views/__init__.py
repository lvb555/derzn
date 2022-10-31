from drevo.views.testirovanie_list_view import TestirovanieListView
from .author_detail_view import AuthorDetailView
from .authors_list_view import AuthorsListView
from .browsing_history import BrowsingHistoryListView
from .comment_page_view import CommentPageView
from .comment_send_view import CommentSendView
from .drevo_list_view import DrevoListView
from .drevo_view import DrevoView
from .expert_work.views import (
    QuestionExpertWorkPage,
    propose_answer,
    update_answer_proposal,
)
from .admin_interview_work.views import (
    AllInterviewView,
    InterviewQuestionsView,
    question_admin_work_view,
)
from .favourite_processing_view import FavouriteProcessView
from .favourites_view import FavouritesView
from .friends_added_view import friends_added_view
from .friends_invite_view import friends_invite_view
from .friends_view import friends_view
from .glossary_list_view import GlossaryListView
from .knowledge_grade_view import KnowledgeFormView
from .labels_list_view import LabelsListView
from .new_knowledge_list_view import NewKnowledgeListView
from .search_author_view import AuthorSearchView
from .search_knowledge_view import KnowledgeSearchView
from .search_tag_view import TagSearchView
from .subscribe_to_author_view import SubscribeToAuthor
from .znanie_by_label_view import ZnanieByLabelView
from .znanie_detail_view import ZnanieDetailView
from .znanie_rating_view import ZnanieRatingView
from .znanie_send_view import send_znanie

__all__ = [
    "SubscribeToAuthor",
    "AuthorDetailView",
    "AuthorsListView",
    "CommentPageView",
    "CommentSendView",
    "DrevoListView",
    "DrevoView",
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
    "BrowsingHistoryListView",
    "FavouritesView",
    "FavouriteProcessView",
    "friends_view",
    "friends_added_view",
    "friends_invite_view",
    "FavouriteProcessView",
    "propose_answer",
    "update_answer_proposal",
    "QuestionExpertWorkPage",
    "send_znanie",
    'TestirovanieListView'
]
