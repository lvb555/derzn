"""
Модуль данных и их загрузки из БД для упрощения логики вьюх
"""

from drevo import models as orm


def load_interview(pk: int) -> dict:
    """
    Загрузка из БД интервью
    """

    interview_type_id = orm.Tz.objects.get(name="Интервью").id
    # bypass 404
    interview_raw = orm.Znanie.objects.get(
        pk=pk, is_published=True, tz_id=interview_type_id
    )
    interview = dict(id=pk, title=interview_raw.name)
    return interview
