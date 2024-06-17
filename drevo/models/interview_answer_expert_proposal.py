from django.contrib.auth import get_user_model
from django.db import models

from drevo.models.knowledge import Znanie
from drevo.models.relation import Relation
from drevo.models.relation_type import Tr

User = get_user_model()


def comment_default_factory():
    """
    Значение по умолчанию для поля comment
    Используется и в модели и формах.
    """
    return dict(arguments=[], counter_arguments=[])


class InterviewAnswerExpertProposal(models.Model):
    """
    Мнение эксперта по ответу на вопрос из интервью.
    Эксперт проходит интервью и создает свои предложения по ответам на вопросы
    или создает свои, новые ответы (что тоже является предложением).
    Вопрос может использоваться в нескольких интервью, потому мы указываем
    ссылку на конкретное.

    В случае же когда мнение является предложением нового ответа, мы должны понять к
    какому вопросу в интервью относится данное предложение, потому, в итоге,
    мы имеем такой набор связей:

    - интервью - предложение в заданном интервью
    - вопрос - предложение по заданному вопросу
    - ответ (опционально) - предложение по заданному ответу. Если null - то это новый ответ.
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

    # ссылка на интервью
    interview = models.ForeignKey(
        to=Znanie,
        on_delete=models.PROTECT,
        related_name="interview_proposals",
        verbose_name="Интервью",
    )

    # реквизит "Ответ" - указатель на сущность "Знания".
    # ссылка на связь между вопросом и интервью. Связь с типом "Состав"
    question = models.ForeignKey(
        to=Znanie,
        on_delete=models.PROTECT,
        related_name="question_proposals",
        verbose_name="Вопрос"
    )
    answer = models.ForeignKey(
        to=Znanie,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="answer_proposals",
        verbose_name="Ответ",
    )

    # реквизит "Некорректная связь" - логический. Некорректная связь – True;
    is_incorrect_answer = models.BooleanField(
        default=False, verbose_name="Некорректный ответ"
    )

    # реквизит "Статус ответа" - логический. Согласен – True; Не согласен -
    # False
    is_agreed = models.BooleanField(
        default=True,
        verbose_name="Эксперт согласен с ответом?",
    )

    # реквизит "Дата/время сессии" – дата/время
    updated = models.DateTimeField(auto_now=True)

    # реквизит "Предложение эксперта" – текстовый. Это текст предложения
    # (нового ответа)
    new_answer_text = models.TextField(
        null=True,
        blank=True,  # чтобы виджеты в админке не требовали ввода
        verbose_name="новый ответ от эксперта",
    )

    # Реквизит "Пояснение некорректности ответа". Данный реквизит будет заполнен экспертом если
    # is_incorrect_answer имеет значение True
    incorrect_answer_explanation = models.TextField(
        verbose_name='Пояснение некорректности ответа',
        blank=True
    )

    # ================================= Admin fields ========================
    # Следующие поля изменяются уже администратором
    # Возможно, будет правильноее не заводить их, а использовать текущие

    # реквизит "Новый ответ" - указатель на сущность "Знания". Это новый ответ,
    # созданный на основе предложения эксперта.
    new_answer = models.OneToOneField(
        to=Znanie,
        null=True,
        blank=True,  # чтобы виджеты в админке не требовали ввода
        on_delete=models.PROTECT,
        related_name="made_in_interview",
        verbose_name="Новый ответ",
    )

    # реквизит "Ответ для дублей" - указатель на сущность "Знания". Это ответ,
    # который устанавливается если предложенный экспертом ответ на вопрос уже существует.
    duplicate_answer = models.ForeignKey(
        to=Znanie,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="duplicate_answer_proposals",
        verbose_name="Ответ для дублей",
    )

    # реквизит "Администратор" - указатель на сущность "Пользователи"
    admin_reviewer = models.ForeignKey(
        User,
        null=True,
        blank=True,  # чтобы виджеты в админке не требовали ввода
        on_delete=models.PROTECT,
        verbose_name="Администратор",
    )

    # реквизит "Комментарий администратора" – текстовый
    admin_comment = models.TextField(
        default="",
        blank=True,  # чтобы виджеты в админке не требовали ввода
        verbose_name="Комментарий администратора",
    )

    # реквизит "Статус предложения" – указатель на перечисление «Статусы предложений».
    status = models.CharField(
        null=True,
        blank=True,  # чтобы виджеты в админке не требовали ввода
        choices=STATUSES,
        max_length=6,
    )

    # реквизит "Уведомлён" - имеет значение True если админ установил статус предложению и отправил результаты
    # интервью эксперту
    is_notified = models.BooleanField(
        verbose_name='Уведомлён',
        default=False
    )

    @staticmethod
    def create_new_proposal(
        expert_user: User,
        interview_id: int,
        question_id: int = None,
        text: str = None,
        is_agreed: bool = False,
        is_incorrect_answer: bool = False,
    ) -> "InterviewAnswerExpertProposal":
        return InterviewAnswerExpertProposal.objects.create(
            new_answer_text=text,
            expert=expert_user,
            interview_id=interview_id,
            question_id=question_id,
            is_agreed=is_agreed,
            is_incorrect_answer=is_incorrect_answer,
        )

    @staticmethod
    def get_actual_proposal(
        expert_pk: int,
        interview_pk: int,
        question_pk: int,
        answer_pk: int = None,
        proposal_pk: int = None,
    ) -> "InterviewAnswerExpertProposal":
        """
        для ответа эксперт может создать только 1 предложение, но из-за
        реляционных связей мы можем иметь несколько вариантов.
        Берем последний - самый актуальный, чтобы взять последние изменения
        (если брать первый, то можно получить некорректное поведение, когда
        при обновлении ничего не меняется, потому что создается новый объект).
        """
        assert (answer_pk or proposal_pk) and "supply answer_pk or  proposal_pk"
        if answer_pk is not None:
            return InterviewAnswerExpertProposal.objects.get(
                answer_id=answer_pk,
                expert_id=expert_pk,
                interview_id=interview_pk,
                question_id=question_pk,
            )
        else:
            return InterviewAnswerExpertProposal.objects.get(pk=proposal_pk)

    def check_max_agreed(prop):
        """
        Контроль максимально разрешенных чекбоксов (с ответом согласен) эксперта
        с ответами и предложениями.
        Возвращает true, если разрешено менять поле is_agree ответов и предложений
        с false на true. Если число ответов и предложений с is_agree=true
        больше max_agreed  - возвращает false.
        """
        usr_id = Znanie.objects.get(id=prop.question_id).user_id
        max_agreed = (
            Relation.objects.filter(
                bz_id=prop.question_id,
                tr_id=Tr.objects.get(name="Число ответов").id,
                user_id=usr_id,
            )
            .order_by()
            .last()
        )
        max_agreed = Znanie.objects.get(id=max_agreed.rz_id)
        if not max_agreed:
            return True
        max_agreed = int(max_agreed.name)
        current_agreed = InterviewAnswerExpertProposal.objects.filter(
            expert_id=usr_id,
            question=prop.question_id,
            interview=prop.interview_id,
            is_agreed=True,
        ).count()

        if max_agreed <= current_agreed:
            return False

        return True

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Предложение эксперта"
        verbose_name_plural = "Предложения эксперта"
        ordering = ("-updated",)
        # 1 Эксперт не может сделать 2 предложения к 1му ответу
        constraints = [
            models.UniqueConstraint(
                fields=["answer", "expert", "interview", "question"],
                name="single_proposal_from_expert_on_answer",
            ),
        ]
