from django.db import models
from users.models import User
from drevo.models.relation import Relation
from drevo.models.relation_grade_scale import RelationGradeScale


class RelationGrade(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name='Пользователь',
    )
    relation = models.ForeignKey(
        Relation,
        on_delete=models.CASCADE,
        related_name='grades',
        verbose_name='Связь',
    )
    grade = models.ForeignKey(
        RelationGradeScale,
        on_delete=models.PROTECT,
        verbose_name='Оценка связи',
    )
    created_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата создания',
    )

    class Meta:
        verbose_name = 'Оценка связи'
        verbose_name_plural = 'Оценки связей'
        unique_together = ('user', 'relation',)
