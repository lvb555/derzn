from django.db import models
from users.models import User
from drevo.models.knowledge import Znanie
from drevo.models.knowledge_grade_scale import KnowledgeGradeScale


class KnowledgeGrade(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name='Пользователь',
    )
    knowledge = models.ForeignKey(
        Znanie,
        on_delete=models.CASCADE,
        related_name='grades',
        verbose_name='Знание',
    )
    grade = models.ForeignKey(
        KnowledgeGradeScale,
        on_delete=models.PROTECT,
        verbose_name='Оценка знания',
    )
    created_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата создания',
    )

    class Meta:
        verbose_name = 'Оценка знания'
        verbose_name_plural = 'Оценки знаний'
        unique_together = ('user', 'knowledge',)
