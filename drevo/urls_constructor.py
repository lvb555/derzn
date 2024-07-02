"""
Модуль с путями для конструкторов знаний
потому что их просто очень много......
"""

from django.urls import path

from drevo.views.knowledge_view import \
    KnowledgeCreateView as KnowledgeCreateViewModal
from drevo.views.zn_constructors.table_constructor_view import (
    TableConstructView, TableFillingView)

from .views import (MainZnInConstructorCreateView, QuizConstructorView,
                    TreeConstructorView, ZnaniyaForConstructorView,
                    answer_create_update_in_quiz, answers_in_quiz_existence,
                    check_algorithm_correctness_from_request,
                    UnprocessedSuggestionsTreeView, answer_create_update_in_quiz,
                    create_zn_for_cell, create_zn_in_tree_constructor,
                    delete_algorithm, delete_answers_or_questions_to_quiz,
                    delete_complex_zn, delete_element_of_relation, delete_quiz,
                    delete_relation_in_tree_constructor, delete_row_or_column,
                    delete_table, delete_zn_in_cell_in_table,
                    edit_main_zn_in_constructor,
                    edit_znanie_in_tree_constructor,
                    element_of_group_in_table_create_update_view,
                    get_answers_to_selected_question_of_quiz,
                    get_cell_for_table, get_order_of_relation,
                    get_rel_zn_in_tree_constructor_from_request,
                    get_tr_for_create_relation_in_tree_constructor,
                    get_tr_for_edit_relation_in_tree_constructor,
                    is_current_user_creator_of_zn, make_copy_of_algorithm,
                    question_create_update_in_quiz,
                    relation_in_table_create_update_view,
                    row_and_column_existence, save_rel_in_tree_constructor,
                    save_zn_to_cell_in_table_from_request,
                    show_filling_tables_page)

urlpatterns = [
    # квиз
    path(
        "question_create_update_in_quiz/",
        question_create_update_in_quiz,
        name="question_create_update_in_quiz",
    ),
    path(
        "answer_create_update_in_quiz/",
        answer_create_update_in_quiz,
        name="answer_create_update_in_quiz",
    ),
    path("delete_quiz/", delete_quiz, name="delete_quiz"),
    path(
        "answers_in_quiz_existence/",
        answers_in_quiz_existence,
        name="answers_in_quiz_existence",
    ),
    # таблица
    path(
        "save_zn_to_cell_in_table_from_request/",
        save_zn_to_cell_in_table_from_request,
        name="save_zn_to_cell_in_table_from_request",
    ),
    path("get_cell_for_table/", get_cell_for_table, name="get_cell_for_table"),
    path(
        "main_znanie_in_constructor_create/<type_of_zn>/",
        MainZnInConstructorCreateView.as_view(),
        name="main_znanie_in_constructor_create",
    ),
    path(
        "znaniya_for_constructor/",
        ZnaniyaForConstructorView.as_view(),
        name="znaniya_for_constructor",
    ),
    path(
        "znaniya_for_suggestions/",
        UnprocessedSuggestionsTreeView.as_view(),
        name="znaniya_for_suggestions",
    ),
    path("delete_table/", delete_table, name="delete_table"),
    path("delete_row_or_column/", delete_row_or_column, name="delete_row_or_column"),
    path(
        "show_filling_tables_page/",
        show_filling_tables_page,
        name="show_filling_tables_page",
    ),
    path(
        "delete_element_of_relation/",
        delete_element_of_relation,
        name="delete_element_of_relation",
    ),
    path(
        "get_answers_to_selected_question_of_quiz/",
        get_answers_to_selected_question_of_quiz,
        name="get_answers_to_selected_question_of_quiz",
    ),
    path(
        "row_and_column_existence/",
        row_and_column_existence,
        name="row_and_column_existence",
    ),
    path(
        "delete_answers_or_questions_to_quiz/",
        delete_answers_or_questions_to_quiz,
        name="delete_answers_or_questions_to_quiz",
    ),
    path(
        "rel_in_tree_constructor/create/",
        get_tr_for_create_relation_in_tree_constructor,
        name="rel_in_tree_constructor_create",
    ),
    # ---------------------------------------------------------------------------------------
    # структура и наполнение таблиц
    path(
        "table_constructor/<int:pk>/",
        TableConstructView.as_view(),
        name="table_constructor",
    ),
    path("filling_tables/<int:pk>/", TableFillingView.as_view(), name="filling_tables"),
    # для вызова модального окна
    path("znanie/add/", KnowledgeCreateViewModal.as_view(), name="knowledge_create"),
    # ---------------------------------------------------------------------------------------
    path(
        "get_rel_zn_in_tree_constructor_from_request/",
        get_rel_zn_in_tree_constructor_from_request,
        name="get_rel_zn_in_tree_constructor_from_request",
    ),
    path(
        "quiz_constructor/<int:pk>/",
        QuizConstructorView.as_view(),
        name="quiz_constructor",
    ),
    path(
        "tree_constructor/<type>/<int:pk>/",
        TreeConstructorView.as_view(),
        name="tree_constructor",
    ),
    path(
        "save_rel_in_tree_constructor/",
        save_rel_in_tree_constructor,
        name="save_rel_in_tree_constructor",
    ),
    path(
        "make_copy_of_algorithm/", make_copy_of_algorithm, name="make_copy_of_algorithm"
    ),
    path(
        "delete_relation_in_tree_constructor/",
        delete_relation_in_tree_constructor,
        name="delete_relation_in_tree_constructor",
    ),
    path(
        "rel_in_tree_constructor/edit/",
        get_tr_for_edit_relation_in_tree_constructor,
        name="rel_in_tree_constructor_edit",
    ),
    path(
        "edit_znanie_in_tree_constructor/",
        edit_znanie_in_tree_constructor,
        name="edit_znanie_in_tree_constructor",
    ),
    path(
        "create_zn_in_tree_constructor/",
        create_zn_in_tree_constructor,
        name="create_zn_in_tree_constructor",
    ),
    path(
        "is_current_user_creator_of_zn/",
        is_current_user_creator_of_zn,
        name="is_current_user_creator_of_zn",
    ),
    path("delete_complex_zn/", delete_complex_zn, name="delete_complex_zn"),
    path("create_zn_for_cell/", create_zn_for_cell, name="create_zn_for_cell"),
    path(
        "check_algorithm_correctness_from_request/",
        check_algorithm_correctness_from_request,
        name="check_algorithm_correctness_from_request",
    ),
    path(
        "relation_in_table_create_update_view/",
        relation_in_table_create_update_view,
        name="relation_in_table_create_update_view",
    ),
    path(
        "element_of_group_in_table_create_update_view/",
        element_of_group_in_table_create_update_view,
        name="element_of_group_create_update_in_table",
    ),
    path(
        "edit_main_zn_in_constructor/",
        edit_main_zn_in_constructor,
        name="edit_main_zn_in_constructor",
    ),
    path("get_order_of_relation/", get_order_of_relation, name="get_order_of_relation"),
    path("delete_algorithm/", delete_algorithm, name="delete_algorithm"),
    path(
        "delete_zn_in_cell_in_table/",
        delete_zn_in_cell_in_table,
        name="delete_zn_in_cell_in_table",
    ),
]
