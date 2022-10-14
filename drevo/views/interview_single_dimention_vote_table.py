from dataclasses import dataclass, field, asdict
from drevo.models import Znanie, Tz, Tr
from django.http.response import HttpResponse
import json


@dataclass
class Question:
    """
    Базовый тип вопроса интервью.
    """

    id: int
    title: str
    type: str


@dataclass
class Answer:
    """
    Ответ на вопрос интервью

    content - текст ответа
    grades - значения оценок ответа
    """

    id: int
    content: str
    grades: list[int] = field(default_factory=list)

    @property
    def avg_grade(self):
        return sum(self.grades) / len(self.grades)


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
    answers: dict[Question, list[Answer]] = field(default_factory=list)


def load_answer(answer_raw: Znanie) -> Answer:
    answer = Answer(id=answer_raw.id, content=answer_raw.name)
    return answer
    # for grade_link in answer_raw.grades.all():
    #     # NOTE: we getting bas_grade (arifmethic avg of max/mix fields)
    #     # so possibly, we need to convert this to just value
    #     value = grade_link.grade.get_base_grade()
    #     answer.grades.append(value)


def load_interview(pk) -> Interview:
    """
    Загрузка из БД структуры Interview
    """

    interview_type_id = Tz.objects.get(name="Интервью").id
    answer_type_id = Tr.objects.get(name="Ответ [ы]").id
    interview_contents_type_id = Tr.objects.get(name="Состав").id
    # bypass 404
    interview_raw = Znanie.objects.get(
        pk=pk, is_published=True, tz_id=interview_type_id
    )

    # TODO: select_related, only
    # interview.base - children
    # interview.related - parents
    # get child links of type 'Состав' - that will be questions
    questions_links = interview_raw.base.filter(tr_id=interview_contents_type_id)

    interview = Interview(title=interview_raw.name)
    for question_link in questions_links:
        # in question link we have rz - related question
        question_raw = question_link.rz

        # make result model of question and fill interview with empty list
        question = Question(title=question_raw.name, type=question_raw.tz.name)

        # get answers of this question
        answers_links = question_raw.base.filter(tr_id=answer_type_id).select_related(
            "rz__name", "rz__id", "rz__grades"
        )
        interview.answers[question] = [
            load_answer(answer_link.rz) for answer_link in answers_links
        ]

    return interview


def interview_vote_table(request, pk):
    """
    Отобржаение одномерной таблицы распределения голосов по ответам эксперта на
    вопросы интервью

    :param pk: идентифиактор интервью
    """

    interview = load_interview(pk)
    return HttpResponse(content=json.dumps(asdict(interview)))
