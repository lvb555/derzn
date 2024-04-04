from django.core.exceptions import ValidationError
from django.db import models
from drevo.models.relation_grade_scale import RelationGradeScale
from users.models import User


class Relation(models.Model):
    """
    Класс для связи Знание-Знание
    """

    title = "Связь"
    # связанное знание
    bz = models.ForeignKey(
        "Znanie",
        on_delete=models.CASCADE,
        verbose_name="Базовое знание",
        help_text="укажите базовое знание",
        related_name="base",
    )
    tr = models.ForeignKey(
        "Tr",
        on_delete=models.CASCADE,
        verbose_name="Вид связи",
        help_text="укажите вид связи",
    )
    rz = models.ForeignKey(
        "Znanie",
        on_delete=models.CASCADE,
        verbose_name="Связанное знание",
        help_text="укажите связанное знание",
        related_name="related",
    )
    author = models.ForeignKey(
        "Author",
        on_delete=models.PROTECT,
        verbose_name="Автор",
        help_text="укажите автора",
    )
    date = models.DateField(
        auto_now_add=True,
        verbose_name="Дата создания",
    )
    user = models.ForeignKey(
        User, on_delete=models.PROTECT, editable=False, verbose_name="Пользователь"
    )
    expert = models.ForeignKey(
        verbose_name="Эксперт",
        to=User,
        on_delete=models.PROTECT,
        related_name="rel_expert",
        null=True,
        blank=True,
    )
    director = models.ForeignKey(
        verbose_name="Руководитель",
        to=User,
        on_delete=models.PROTECT,
        related_name="rel_director",
        null=True,
        blank=True,
    )
    is_published = models.BooleanField(default=False, verbose_name="Опубликовано?")
    order = models.IntegerField(
        verbose_name="Порядок",
        help_text="укажите порядковый номер",
        null=True,
        blank=True,
    )
    meta_info = models.CharField(
        max_length=1024, blank=True, null=True, verbose_name="Метаинформация"
    )

    objects = models.Manager()

    def __str__(self):
        return f"{self.pk} {self.bz} | {self.rz}"

    def get_grouped_relations(self):
        return list(
            sorted(
                self.rz.base.all(),
                key=lambda x: x.rz.order if x.rz.order else 0,
                reverse=True,
            )
        )

    def clean(self):
        if self.bz == self.rz:
            raise ValidationError("Нельзя связать одиннаковые знания.")

    class Meta:
        verbose_name = "Связь"
        verbose_name_plural = "Связи"
        ordering = ("-date",)
        constraints = (
            models.UniqueConstraint(
                fields=("bz", "tr", "rz"),
                name="bz_tr_rz_unique_constraint",
            ),
        )

    def get_proof_grade(self, request, variant):
        """Значение оценки довода (ЗОД)
            request - словарь с параметрами запроса
            variant - вариант оценки: 1 - прямая оценка знания, 2 - общая оценка знания
            = оценка связи н* оценка знания
        """

        # получаем оценку знания - общую или прямую (если есть)
        if variant == 2:
            related_knowledge_grade, _ = self.rz.get_common_grades(request)
        else:
            related_knowledge_grade = self.rz.get_users_grade(request.user)

        # получаем оценку связи
        grades = self.grades.filter(user=request.user)
        if grades.exists():
            relation_grade = grades.first().grade.get_base_grade()
        else:
            relation_grade = RelationGradeScale.objects.first().get_base_grade()

        return (
            related_knowledge_grade * relation_grade
            if related_knowledge_grade is not None
            else None
        )

    def get_proof_weight(self, request, variant):
        """Оценка вклада довода (ОВД)"""
        proof_grade = self.get_proof_grade(request, variant)

        if proof_grade and proof_grade >= 0:
            # Если ЗОД имеет реальное значение, тогда расчет ОВД проводится по формуле.
            # Если расчета нет, то ОВД равен None.

            # Так как argument_type ЗА почему то False, а против - True
            # то определяем знак связи Аргумент-Контраргумент вот так
            argument_sign = -1 if self.tr.argument_type else 1
            return proof_grade * argument_sign
        else:
            return None

    @staticmethod
    def get_default_grade():
        return RelationGradeScale.objects.all().first().get_base_grade()
