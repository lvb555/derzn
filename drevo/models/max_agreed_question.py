from django.db import models
from drevo.models import Znanie
from users.models import User

class MaxAgreedQuestion(models.Model):
    """
    Счетчик максимального числа согласий с ответами + предложениями
    (собственные ответы) для чекбокса С ответом согласен
    набор связей:

    - интервью - предложение в заданном интервью
    - вопрос - предложение по заданному вопросу
    - max_agreed (опционально) - максимальное число согласий экперта
    с ответами на вопрос. null - ограничения нет
    """

    # ссылка на интервью
    interview = models.ForeignKey(
        to=Znanie,
        on_delete=models.PROTECT,
        related_name="max_agreed_interview",
        verbose_name="Интервью",
    )

    question = models.ForeignKey(
        to=Znanie,
        on_delete=models.PROTECT,
        related_name="max_agreed_question",
        verbose_name="Вопрос",
    )

    author = models.ForeignKey(User,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="max_agreed_author",
        verbose_name="Автор"
    )

    # реквизит "Max_agreed" - числовой (integer). Максимальное число согласий
    # с ответами на вопрос
    max_agreed = models.IntegerField(
        null=True,
        blank=True,  # чтобы виджеты в админке не требовали ввода
        verbose_name="Максимальное число согласий c ответами на вопрос",
    )


    class Meta:
            constraints = [
                models.UniqueConstraint(
                    fields=["interview", "question", "author"],
                    name="single_max_agreed_from_expert_on_question_interview",
                ),
            ]
