from .author_detail_view import AuthorDetailView
from .authors_list_view import AuthorsListView
from .comment_page_view import CommentPageView
from .comment_send_view import CommentSendView
from .drevo_list_view import DrevoListView
from .drevo_view import DrevoView
from .glossary_list_view import GlossaryListView
from .labels_list_view import LabelsListView
from .znanie_by_label_view import ZnanieByLabelView
from .znanie_detail_view import ZnanieDetailView
from .znanie_rating_view import ZnanieRatingView
from .search_knowledge_view import KnowledgeSearchView
from .search_author_view import AuthorSearchView
from .search_tag_view import TagSearchView
from .knowledge_grade_view import KnowledgeFormView
from .new_knowledge_list_view import NewKnowledgeListView
from .browsing_history import BrowsingHistoryListView
from .subscribe_to_author_view import SubscribeToAuthor
from .favourites_view import FavouritesView
from .favourite_processing_view import FavouriteProcessView
from .friends_added_view import friends_added_view
from .friends_view import friends_view
from .friends_invite_view import friends_invite_view
from .knowledge_grade_statistic_view import KnowledgeStatisticFormView


__all__ = [
    'SubscribeToAuthor',
    'AuthorDetailView',
    'AuthorsListView',
    'CommentPageView',
    'CommentSendView',
    'DrevoListView',
    'DrevoView',
    'GlossaryListView',
    'LabelsListView',
    'ZnanieByLabelView',
    'ZnanieDetailView',
    'ZnanieRatingView',
    'NewKnowledgeListView',
    'KnowledgeSearchView',
    'AuthorSearchView',
    'TagSearchView',
    'KnowledgeFormView',
    'BrowsingHistoryListView',
    'FavouritesView',
    'FavouriteProcessView',
    'friends_view',
    'friends_added_view',
    'friends_invite_view',
    'KnowledgeStatisticFormView'
]
