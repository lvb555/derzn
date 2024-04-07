from django.db import models
from django.db.models import Q
from django.urls import reverse
from mptt.models import TreeForeignKey

from drevo.common import variables
from users.models import User
from .category import Category
from .knowledge_grade_scale import KnowledgeGradeScale
from .knowledge_rating import ZnRating
from ..managers import ZManager


class Znanie(models.Model):
    """
    Класс для описания сущности 'Знание'
    """

    title = "Знание"
    name = models.CharField(max_length=255, verbose_name="Тема", unique=True)
    category = TreeForeignKey(
        Category,
        on_delete=models.PROTECT,
        verbose_name="Категория",
        null=True,
        blank=True,
        limit_choices_to={"is_published": True},
    )
    tz = models.ForeignKey("Tz", on_delete=models.PROTECT, verbose_name="Вид знания")
    content = models.TextField(
        max_length=2048, blank=True, null=True, verbose_name="Содержание"
    )
    href = models.URLField(
        max_length=256,
        verbose_name="Источник",
        help_text="укажите www-адрес источника",
        null=True,
        blank=True,
    )
    source_com = models.CharField(
        max_length=256, verbose_name="Комментарий к источнику", null=True, blank=True
    )
    author = models.ForeignKey(
        "Author",
        on_delete=models.PROTECT,
        verbose_name="Автор",
        help_text="укажите автора",
        null=True,
        blank=True,
    )
    date = models.DateField(
        auto_now_add=True,
        verbose_name="Дата создания",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата и время редактирования",
    )
    user = models.ForeignKey(
        User, on_delete=models.PROTECT, editable=False, verbose_name="Пользователь"
    )
    expert = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="knowledge_expert",
        verbose_name="Эксперт",
    )
    redactor = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="redactor",
        verbose_name="Редактор",
    )
    director = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="director",
        verbose_name="Руководитель",
    )
    order = models.IntegerField(
        verbose_name="Порядок",
        help_text="укажите порядковый номер",
        null=True,
        blank=True,
    )

    is_published = models.BooleanField(default=False, verbose_name="Опубликовано?")
    labels = models.ManyToManyField("Label", verbose_name="Метки", blank=True)
    is_send = models.BooleanField(verbose_name="Пересылать", default=True)
    show_link = models.BooleanField(
        verbose_name="Отображать как ссылку?",
        default=True,
    )
    notification = models.BooleanField(default=False, verbose_name="Уведомления")
    several_works = models.BooleanField(default=False, verbose_name="Несколько работ")

    meta_info = models.CharField(
        max_length=1024, blank=True, null=True, verbose_name="Метаинформация"
    )

    # Для обработки записей (сортировка, фильтрация) вызывается собственный Manager,
    # в котором уже установлена фильтрация по is_published и сортировка
    objects = models.Manager()
    published = ZManager()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("zdetail", kwargs={"pk": self.pk})

    def voting(self, user, value):
        rating_obj = self.znrating_set.filter(user=user).first()

        if rating_obj:
            if value == rating_obj.value:
                rating_obj.value = ZnRating.BLANK
            else:
                rating_obj.value = value

            rating_obj.save()
        else:
            ZnRating.objects.create(znanie=self, user=user, value=value)

    def get_users_vote(self, user):
        rating_obj = self.znrating_set.filter(user=user).first()

        if rating_obj:
            if rating_obj.value in (ZnRating.LIKE, ZnRating.DISLIKE):
                return rating_obj.value

        return None

    def get_likes_count(self):
        return self.znrating_set.filter(value=ZnRating.LIKE).count()

    def get_dislikes_count(self):
        return self.znrating_set.filter(value=ZnRating.DISLIKE).count()

    def get_comments_count(self):
        return self.comments.filter(parent=None).count()

    def get_users_grade(self, user: User) -> float | None:
        """
        Оценка пользователя user.
        По умолчанию -  None
        """

        knowledge_grade = self.grades.filter(user=user).first()
        if knowledge_grade:
            return knowledge_grade.grade.get_base_grade()
        else:
            return None

    def get_common_grades(self, request) -> tuple[float | None, float | None]:
        """
        Расчёт общей оценки знания.
        Возвращает числовое значение общей оценки и
        числовое значение оценки доказательной базы (ОДБ).
        """

        variant = request.GET.get("variant")
        if variant and variant.isdigit():
            variant = int(variant)
        else:
            variant = 1

        proof_base_value = self.get_proof_base_grade(request, variant)
        if proof_base_value is not None:
            users_grade = self.get_users_grade(request.user)
            if users_grade is not None:
                common_grade_value = (proof_base_value + users_grade) / 2
            else:
                common_grade_value = None
        else:
            common_grade_value = self.get_users_grade(request.user)

        return common_grade_value, proof_base_value

    def get_proof_base_grade(self, request, variant) -> float | None:
        """
        Возвращает числовое значение оценки доказательной базы
        как среднее от всех ненулевых оценок
        в зависимости от варианта
            1 - оценка берется не дальше аргументов
            2 - оценка берется по всему дереву базы
        """

        sum_list = []

        queryset = self.base.filter(
            tr__is_argument=True,
            rz__tz__can_be_rated=True,
        )
        if queryset.exists():
            for relation in queryset:
                grade = relation.get_proof_weight(request, variant)

                if grade:
                    sum_list.append(grade)

        if not sum_list:
            # Если доводов нет, Тогда ОДБ := None
            return None

        # ОДБ := среднее арифметическое Оценок вкладов доводов (ОВД) среди существенных доводов..
        proof_base_value = sum(sum_list) / len(sum_list)

        return proof_base_value

    @staticmethod
    def get_default_grade() -> KnowledgeGradeScale:
        """Возвращает оценку по умолчанию"""
        return KnowledgeGradeScale.get_default_grade()

    def get_ancestors_category(self):
        """
        Возвращает TreeQuerySet с категорией и предками категории данного знания
        """
        return self.category.get_ancestors(ascending=False, include_self=True)

    def get_expert(self):
        """
        Возвращает список экспертов по данному знанию
        """
        categories = self.get_ancestors_category()
        expert_list = []
        for category in categories:
            experts = category.get_experts()
            if not experts:
                continue
            for expert in experts:
                expert_list.append(expert.expert)
        return expert_list

    @property
    def get_current_status(self):
        """
        Возвращает текущий статус знания
        """
        return self.knowledge_status.get(Q(knowledge=self) & Q(is_active=True))

    def get_status_history(self):
        """
        Возвращает все статусы текущего знания
        """
        return self.knowledge_status.filter(knowledge=self).select_related()

    def get_status_action(self, user: User):
        """
        Возвращает список кортежей с возможным действием для изменения статуса и новым статусом
        :param user: Экземпляр класса модели пользователя
        """
        if user.is_director:
            return variables.TRANSITIONS_DIRECT[self.get_current_status()]
        elif user.is_redactor:
            return variables.TRANSITIONS_RED[self.get_current_status()]
        elif user.is_expert:
            return variables.TRANSITIONS_EXP[self.get_current_status()]
        else:
            return variables.TRANSITIONS_PUB[self.get_current_status()]

    class Meta:
        verbose_name = "Знание"
        verbose_name_plural = "Знания"
        ordering = ("order",)
