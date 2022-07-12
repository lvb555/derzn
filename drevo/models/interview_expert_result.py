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

    title = "Предложение эксперта"

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
        verbose_name="Аргумент вопроса Да-Нет? (нет - контраргумент)"
    )

    # реквизит "Ответ" - указатель на сущность "Знания".
    answer = models.ForeignKey(
        to=Znanie,
        on_delete=models.PROTECT,
        related_name="as_answer_interviews",
        verbose_name="Ответ",
    )

    # реквизит "Некорректная связь" - логический. Некорректная связь – True;
    is_incorrect_answer = models.BooleanField(verbose_name="некорректный ответ")

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
    # список аргументов или контраргументов
    comment = models.TextField(verbose_name="Текст дополнения")

    # реквизит "Дата/время сессии" – дата/время
    updated = models.DateTimeField()

    # реквизит "Предложение эксперта" – текстовый. Это текст предложения
    # (нового ответа)
    new_answer_text = models.TextField(verbose_name="новый ответ от эксперта")

    # реквизит "Новый ответ" - указатель на сущность "Знания". Это новый ответ,
    # созданный на основе предложения эксперта.
    new_answer = models.OneToOneField(
        to=Znanie,
        on_delete=models.PROTECT,
        related_name="made_in_interview",
        verbose_name="Новый ответ",
    )

    # реквизит "Администратор" - указатель на сущность "Пользователи"
    admin_reviewer = models.ForeignKey(
        User, on_delete=models.PROTECT, verbose_name="Администратор"
    )

    # реквизит "Комментарий администратора" – текстовый
    admin_comment = models.TextField(verbose_name="Комментарий администратора")

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

    class Meta:
        verbose_name = "Ответ на интервью"
        verbose_name_plural = "Ответы на интервью"
        ordering = ("-updated",)
