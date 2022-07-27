from django.db import models

from drevo.models.knowledge import Znanie
from django.contrib.auth import get_user_model

User = get_user_model()


class InterviewAnswerExpertProposal(models.Model):
    """
    Предложение эксперта по ответу на вопрос из интервью.
    Эксперт проходит интервью и создает свои предложения по ответам на вопросы
    или создает свои, новые ответы (что тоже является предложением).
    """

    DESCRIPTION_TYPE = (
        ("ARGUM", "Аргумент"),
        ("KONTR", "Контраргумент"),
        ("INVAL", "Некорректность"),
    )

    STATUSES = (
        ("APPRVE", "Принят"),
        ("REJECT", "Не принят"),
        ("ANSDPL", "Дублирует ответ"),
        ("RESDPL", "Дублирует предложение"),
    )
    # реквизит "Эксперт" - указатель на сущность "Пользователи"
    expert = models.ForeignKey(
        to=User,
        on_delete=models.PROTECT,
        related_name="interview_results",
        verbose_name="Ответивший эксперт",
    )

    # реквизит "Группа ответов" - логический. Аргументы (ответ "Да") – True;
    # Контраргументы (ответ "Нет") – False
    is_yesno_answer_argument = models.BooleanField(
        default=False, verbose_name="Аргумент вопроса Да-Нет? (нет - контраргумент)"
    )

    # ссылка на интервью
    interview = models.ForeignKey(
        to=Znanie,
        on_delete=models.PROTECT,
        related_name="interview_proposals",
        verbose_name="Интервью",
    )

    # реквизит "Ответ" - указатель на сущность "Знания".
    # ссылка на связь между вопросом и интервью. Связь с типом "Состав"
    answer = models.ForeignKey(
        to=Znanie,
        null=True,
        on_delete=models.PROTECT,
        related_name="answer_proposals",
        verbose_name="Ответ",
    )

    # реквизит "Некорректная связь" - логический. Некорректная связь – True;
    is_incorrect_answer = models.BooleanField(
        default=False, verbose_name="некорректный ответ"
    )

    # реквизит "Статус ответа" - логический. Согласен – True; Не согласен -
    # False
    is_agreed = models.BooleanField(
        default=True, verbose_name="Эксперт согласен с ответом?", name="согласен"
    )

    # реквизит "Текст дополнения" – текстовый.
    # список аргументов или контраргументов
    # для получения полей используейте getters ниже (get_arguments, get_counter_arguments)
    comment = models.JSONField(
        default=dict, verbose_name="Аргументы и контраргументы (JSON)"
    )

    # реквизит "Дата/время сессии" – дата/время
    updated = models.DateTimeField(auto_now=True)

    # реквизит "Предложение эксперта" – текстовый. Это текст предложения
    # (нового ответа)
    new_answer_text = models.TextField(
        null=True, verbose_name="новый ответ от эксперта"
    )

    # ================================= Admin fields ========================
    # Следующие поля изменяются уже администратором
    # Возможно, будет правильноее не заводить их, а использовать текущие

    # реквизит "Новый ответ" - указатель на сущность "Знания". Это новый ответ,
    # созданный на основе предложения эксперта.
    new_answer = models.OneToOneField(
        to=Znanie,
        null=True,
        on_delete=models.PROTECT,
        related_name="made_in_interview",
        verbose_name="Новый ответ",
    )

    # реквизит "Администратор" - указатель на сущность "Пользователи"
    admin_reviewer = models.ForeignKey(
        User, null=True, on_delete=models.PROTECT, verbose_name="Администратор"
    )

    # реквизит "Комментарий администратора" – текстовый
    admin_comment = models.TextField(
        default="", verbose_name="Комментарий администратора"
    )

    # реквизит "Статус предложения" – указатель на перечисление «Статусы предложений».
    status = models.CharField(
        null=True,
        choices=STATUSES,
        max_length=6,
    )

    @staticmethod
    def create_new_answer(
        expert_user, text: str, comment: str = "{}"
    ) -> "InterviewAnswerExpertProposal":
        return InterviewAnswerExpertProposal.objects.create(
            new_answer_text=text, expert=expert_user, comment=comment
        )

    def get_arguments(self) -> list[str]:
        return self.comment.get("arguments", [])

    def get_counter_arguments(self) -> list[str]:
        return self.comment.get("counter_arguments", [])

    class Meta:
        verbose_name = "Предложение эксперта"
        verbose_name_plural = "Предложения эксперта"
        ordering = ("-updated",)
