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

    @staticmethod
    def get_proof_base_grade(knowledge, user, is_general=True, sum_list=None, base_flag=True):
        if sum_list is None:
            sum_list = []

        queryset = knowledge.base.filter(
            tr__is_argument=True,
            rz__tz__can_be_rated=True,
        )
        summ = 0
        if queryset.exists():
            sum_list.append(sum(map(lambda x: x.get_proof_weight(user), queryset)) / len(queryset))

            if is_general:
                for relation in queryset:
                    child_list = KnowledgeGrade.get_proof_base_grade(
                        relation.rz, user, sum_list=sum_list, base_flag=False
                    )
                    cl = list(filter(lambda x: x > 0, child_list))
                    if cl:
                        summ += sum(cl) / len(cl)
                if summ:
                    sum_list.append(summ)

        if base_flag:
            sum_list = list(filter(lambda x: x > 0, sum_list))
            if sum_list:
                return sum(sum_list) / len(sum_list)
            else:
                return 0
        return [summ]
