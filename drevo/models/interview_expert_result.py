from django.db import models
from django.utils import timezone
from drevo.models.knowledge import Znanie
from django.contrib.auth import get_user_model

User = get_user_model()


class InterviewExpertResult(models.Model):
    """
    Интервью с экспертом.
    Цель интервью - уточнение собранных знаний-вопросов/знаний-ответов.
    Существующие вопросы и ответы собираются в интервью и предлагаются эксперту.
    Эксперт отвечает на вопросы.
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
    respondent = models.ForeignKey(
        to=User, on_delete=models.PROTECT, related_name="interview_results"
    )

    # реквизит "Интервью" - указатель на сущность "Знания". Это метазнание вида
    # "Интервью".
    interview = models.ForeignKey(
        to=Znanie,
        on_delete=models.PROTECT,
        related_name="expert_results",
    )

    # реквизит "Вопрос" - указатель на сущность "Знания". Это знание вида
    # "Вопрос". "Тезис". "Вопрос «Да-Нет".
    question = models.ForeignKey(
        to=Znanie, on_delete=models.PROTECT, related_name="as_question_interviews"
    )

    # реквизит "Группа ответов" - логический. Аргументы (ответ "Да") – True;
    # Контраргументы (ответ "Нет") – False
    answer_group = models.BooleanField()

    # реквизит "Ответ" - указатель на сущность "Знания".
    answer = models.ForeignKey(
        to=Znanie, on_delete=models.PROTECT, related_name="as_answer_interviews"
    )

    # реквизит "Некорректная связь" - логический. Некорректная связь – True;
    is_incorrect_relation = models.BooleanField(verbose_name="не корректная связь")

    # реквизит "Статус ответа" - логический. Согласен – True; Не согласен -
    # False
    is_agreed = models.BooleanField(
        verbose_name="Эксперт согласен с ответом?", name="согласен"
    )

    # реквизит "Вид текста" - Перечисление (Аргумент; Контраргумент;
    # Некорректность)
    comment_type = models.CharField(
        verbose_name="тип комментария", choices=DESCRIPTION_TYPE, max_length=5
    )

    # реквизит "Текст дополнения" – текстовый.
    comment = models.TextField()

    # реквизит "Дата/время сессии" – дата/время
    updated = models.DateTimeField()

    # реквизит "Ответ/Новый ответ" := Вид блока. Если (это блок "Ответ"?; True;
    # False)
    is_new_answer = models.BooleanField(
        verbose_name="Это ответ предложенный экспертом?"
    )

    # реквизит "Предложение эксперта" – текстовый. Это текст предложения
    # (нового ответа)
    new_answer_text = models.TextField(verbose_name="новый ответ от эксперта")

    # реквизит "Новый ответ" - указатель на сущность "Знания". Это новый ответ, созданный на основе предложения эксперта.
    new_answer = models.OneToOneField(
        to=Znanie, on_delete=models.PROTECT, related_name="made_in_interview"
    )

    # реквизит "Администратор" - указатель на сущность "Пользователи"
    admin_reviewer = models.ForeignKey(User, on_delete=models.PROTECT)

    # реквизит "Комментарий администратора" – текстовый
    admin_comment = models.TextField()

    # реквизит "Статус предложения" – указатель на перечисление «Статусы предложений».
    status = models.CharField(
        choices=STATUSES,
        max_length=6,
    )

    def save(self, *args, **kwargs):
        """On save, update timestamp"""
        # also note this:
        # https://stackoverflow.com/questions/1737017/django-auto-now-and-auto-now-add
        self.modified = timezone.now()
        return super(User, self).save(*args, **kwargs)
