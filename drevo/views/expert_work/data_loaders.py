"""
Модуль данных и их загрузки из БД для упрощения логики вьюх
"""
import typing as t
from dataclasses import dataclass, field
from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist

from drevo import models as orm


@dataclass
class User:
    id: int
    username: str


@dataclass
class ExpertProposal:
    """
    Предложение эксперта
    """

    id: int
    is_agreed: bool
    is_incorrect_answer: bool
    updated: datetime
    # Возможное предложение нового ответа от эксперта
    text: t.Optional[str] = None
    args: list[str] = field(default_factory=list)
    counter_args: list[str] = field(default_factory=list)


@dataclass
class Question:
    """
    Базовый тип вопроса интервью.
    """

    id: int
    title: str

    def __hash__(self):
        return self.id


@dataclass
class AnswerProposal:
    """
    Ответ на вопрос интервью

    content - текст ответа
    propsal
    """

    id: int
    text: str
    is_agreed: bool = False
    is_incorrect_answer: bool = False


@dataclass
class Interview:
    """
    Представление данных интервью для текущей задачи

    title -  тема интервью.
    answers - словарь ответов на вопросы. Каждая пара (ключ, значения) это
    вопров и ответы на него
    """

    id: int
    title: str
    answers: dict[Question, list[AnswerProposal]] = field(default_factory=dict)


def load_answer_proposals(
    answer_raw: orm.Znanie, expert_pk: int, interview_pk: int
) -> AnswerProposal:
    """
    Загрузка ответа с предложением эксперта к этому ответу
    """
    answer = AnswerProposal(id=answer_raw.pk, text=answer_raw.name)
    # TODO: загрузить все и показать выбранный по HTTP параметрам ответ эксперта
    # Если 1 эксперт может создавать более 1 предложения по 1 вопросу, то нужно показать
    # послединй и на UI дать возможность выбрать "версию" для редактирования.
    try:
        proposal_raw = orm.InterviewAnswerExpertProposal.get_actual_proposal(
            expert_pk=expert_pk, answer_pk=answer_raw.pk, interview_pk=interview_pk
        )
    except ObjectDoesNotExist:
        pass
    else:
        answer.is_agreed = proposal_raw.is_agreed
        answer.is_incorrect = proposal_raw.is_incorrect_answer

    return answer


def load_interview(pk: int) -> Interview:
    """
    Загрузка из БД интервью
    """

    interview_type_id = orm.Tz.objects.get(name="Интервью").id

    # bypass 404
    interview_raw = orm.Znanie.objects.get(
        pk=pk, is_published=True, tz_id=interview_type_id
    )
    interview = Interview(id=pk, title=interview_raw.name)
    return interview
